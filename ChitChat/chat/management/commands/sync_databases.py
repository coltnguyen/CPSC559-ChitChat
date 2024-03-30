from django.core.management.base import BaseCommand
from pymongo import MongoClient, UpdateOne, DeleteMany
from pymongo.errors import BulkWriteError
import logging
import hashlib
import datetime

def run_synchronization():
    command = Command()
    command.handle()

class Command(BaseCommand):
    help = 'Forcefully synchronizes data both databases.'

    def document_hash(self, document):
        # Create a copy to avoid modifying the original document
        doc_copy = document.copy()
        doc_copy.pop('_id', None)
        # Convert the document to a string and hash it
        doc_string = str(doc_copy).encode('utf-8')
        return hashlib.sha256(doc_string).hexdigest()

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting synchronization process...'))
        try:
            # Connect to both databases
            main_db_client = MongoClient('mongodb+srv://coltvnguyen:Legitpassword12@chitchat-cluster-1.gjvrsgz.mongodb.net/?retryWrites=true&w=majority')
            replica_db_client = MongoClient('mongodb+srv://coltvnguyen:Legitpassword12@chitchat-cluster-1.gjvrsgz.mongodb.net/?retryWrites=true&w=majority')
            main_db = main_db_client['chitchat_db']
            replica_db = replica_db_client['chitchat_db_replica']

            # Get the last successful synchronization timestamp
            last_sync_timestamp = self.get_last_sync_timestamp(main_db)

            # Synchronize from main to replica
            self.sync_databases(source_db=main_db, target_db=replica_db, last_sync_timestamp=last_sync_timestamp)

            # Synchronize from replica to main (if needed)
            self.sync_databases(source_db=replica_db, target_db=main_db, last_sync_timestamp=last_sync_timestamp)

            # Update the last successful synchronization timestamp
            self.update_last_sync_timestamp(main_db)

            self.stdout.write(self.style.SUCCESS('Synchronization completed successfully.'))
        except Exception as e:
            logging.error(f"Error during synchronization: {e}")
            self.stdout.write(self.style.ERROR('Synchronization failed.'))

    def get_last_sync_timestamp(self, db):
        sync_collection = db['sync_info']
        sync_info = sync_collection.find_one()
        if sync_info:
            return sync_info['last_sync_timestamp']
        return None

    def update_last_sync_timestamp(self, db):
        sync_collection = db['sync_info']
        current_timestamp = datetime.datetime.now()
        sync_collection.update_one({}, {'$set': {'last_sync_timestamp': current_timestamp}}, upsert=True)

    def sync_databases(self, source_db, target_db, last_sync_timestamp):
        include_collections = ['chat_message', 'chat_user']
        exclude_collections = ['__schema__', 'django_migrations']  # Add any other collections to exclude

        collection_names = [name for name in source_db.list_collection_names() if name in include_collections and name not in exclude_collections]

        inconsistencies_found = False

        for collection_name in collection_names:
            print(f"Synchronizing collection: {collection_name}")  # Print the collection being synchronized
            source_collection = source_db[collection_name]
            target_collection = target_db[collection_name]

            source_ids = set()
            bulk_operations = []  # Reset bulk operations for each collection

            query = {}
            if last_sync_timestamp:
                query['updated_at'] = {'$gt': last_sync_timestamp}

            for source_document in source_collection.find(query):
                document_id = source_document.get('id')
                if document_id is not None:
                    source_ids.add(document_id)
                    source_document.pop('_id', None)

                    target_document = target_collection.find_one({'id': document_id})
                    if target_document:
                        target_document.pop('_id', None)

                        source_doc_hash = self.document_hash(source_document)
                        target_doc_hash = self.document_hash(target_document)

                        if source_doc_hash != target_doc_hash:
                            print(f"Difference found for document id: {document_id} in collection: {collection_name}. Updating in target database.")
                            bulk_operations.append(UpdateOne({'id': document_id}, {'$set': source_document}, upsert=True))
                            inconsistencies_found = True
                    else:
                        print(f"Document id: {document_id} not found in target database collection: {collection_name}. Inserting.")
                        bulk_operations.append(UpdateOne({'id': document_id}, {'$set': source_document}, upsert=True))
                        inconsistencies_found = True

            # Execute bulk operations for the current collection
            if bulk_operations:
                try:
                    # Start the two-phase commit
                    with target_db.client.start_session() as session:
                        with session.start_transaction():
                            result = target_collection.bulk_write(bulk_operations, session=session)
                            print(f"Bulk operations result for collection '{collection_name}': {result.bulk_api_result}")
                            session.commit_transaction()
                except BulkWriteError as e:
                    print(f"Error during bulk operations for collection '{collection_name}': {e}")
                    # Handle specific errors or retry logic here
                except Exception as e:
                    print(f"Error during synchronization for collection '{collection_name}': {e}")
                    raise

        if not inconsistencies_found:
            print("No inconsistencies found.")

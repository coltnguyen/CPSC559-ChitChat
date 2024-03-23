from django.core.management.base import BaseCommand
from pymongo import MongoClient, UpdateOne, DeleteMany
from pymongo.errors import BulkWriteError
import logging
import hashlib

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

            # Synchronize from main to replica
            self.sync_databases(source_db=main_db, target_db=replica_db)

            # Synchronize from replica to main (if needed)
            self.sync_databases(source_db=replica_db, target_db=main_db)

            self.stdout.write(self.style.SUCCESS('Synchronization completed successfully.'))
        except Exception as e:
            logging.error(f"Error during synchronization: {e}")
            self.stdout.write(self.style.ERROR('Synchronization failed.'))

    def sync_databases(self, source_db, target_db):
        include_collections = ['chat_message', 'chat_user']

        exclude_collections = ['__schema__', 'django_migrations']  # Add any other collections to exclude

        collection_names = [name for name in source_db.list_collection_names() if name in include_collections and name not in exclude_collections]

        for collection_name in collection_names:
            print(f"Synchronizing collection: {collection_name}")  # Print the collection being synchronized

            source_collection = source_db[collection_name]
            target_collection = target_db[collection_name]

            source_ids = set()

            bulk_operations = []  # Reset bulk operations for each collection

            for source_document in source_collection.find():

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
                    else:
                        print(f"Document id: {document_id} not found in target database collection: {collection_name}. Inserting.")
                        bulk_operations.append(UpdateOne({'id': document_id}, {'$set': source_document}, upsert=True))

            # # Remove documents from the target database that don't exist in the source database
            # target_ids = set(doc['id'] for doc in target_collection.find({}, {'id': 1}))
            # ids_to_remove = target_ids - source_ids
            # if ids_to_remove:
            #     print(f"Removing documents with ids: {ids_to_remove} from target database collection: {collection_name}.")
            #     bulk_operations.append(DeleteMany({'id': {'$in': list(ids_to_remove)}}))

            # Execute bulk operations for the current collection
            if bulk_operations:
                try:
                    result = target_collection.bulk_write(bulk_operations)
                    print(f"Bulk operations result for collection '{collection_name}': {result.bulk_api_result}")
                except BulkWriteError as e:
                    print(f"Error during bulk operations for collection '{collection_name}': {e}")
                    # Handle specific errors or retry logic here
                except Exception as e:
                    print(f"Error during synchronization for collection '{collection_name}': {e}")
                    raise


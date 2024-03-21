from django.core.management.base import BaseCommand
from pymongo import MongoClient, UpdateOne, DeleteMany
from pymongo.errors import BulkWriteError
import logging
import hashlib

class Command(BaseCommand):
    help = 'Synchronizes data between the main MongoDB and its replica.'

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
        exclude_collections = ['__schema__', 'django_migrations'] # Add any other collections to exclude
        bulk_operations = []

        # Filter the collection names to only include those in the include_collections list
        collection_names = [name for name in source_db.list_collection_names() if name in include_collections and name not in exclude_collections]

        for collection_name in collection_names:
            print(f"Synchronizing collection: {collection_name}") # Print the collection being synchronized
            source_collection = source_db[collection_name]
            target_collection = target_db[collection_name]

            source_ids = set()

            for source_document in source_collection.find():
                print(f"Processing document: {source_document}") # Print each document being processed
                document_id = source_document.get('id')
                if document_id is not None:
                    source_ids.add(document_id)
                    source_document.pop('_id', None)

                    target_document = target_collection.find_one({'id': document_id})
                    if target_document:
                        target_document_no_id = target_document.copy()
                        target_document_no_id.pop('_id', None)

                        source_doc_hash = self.document_hash(source_document)
                        target_doc_hash = self.document_hash(target_document_no_id)

                        if source_doc_hash != target_doc_hash:
                            print(f"Updating document with id: {document_id} in collection: {collection_name}") # Print when a document is updated
                            bulk_operations.append(UpdateOne({'id': document_id}, {'$set': source_document}, upsert=True))
                    else:
                        print(f"Inserting document with id: {document_id} in collection: {collection_name}") # Print when a document is inserted
                        bulk_operations.append(UpdateOne({'id': document_id}, {'$set': source_document}, upsert=True))
                else:
                    # Handle documents without an 'id' field
                    print(f"Skipping document without 'id' field in collection: {collection_name}") # Print when a document is skipped
                    logging.warning(f"Skipping document without 'id' field: {source_document}")

            # Remove documents from the target database that don't exist in the source database
            target_ids = set(doc['id'] for doc in target_collection.find({}, {'id': 1}))
            ids_to_remove = target_ids - source_ids
            if ids_to_remove:
                print(f"Removing documents with ids: {ids_to_remove} from collection: {collection_name}") # Print when documents are removed
                bulk_operations.append(DeleteMany({'id': {'$in': list(ids_to_remove)}}))

        try:
            if bulk_operations:
                print(f"Executing bulk operations for collection: {collection_name}") # Print before executing bulk operations
                target_db[collection_name].bulk_write(bulk_operations)
        except BulkWriteError as e:
            # Handle duplicate key errors
            for error in e.details['writeErrors']:
                if error['code'] == 11000: # Duplicate key error code
                    print(f"Duplicate key error: {error}") # Print the error details
                    duplicate_id = error['keyValue']['id']
                    target_collection.delete_one({'id': duplicate_id})
                    bulk_operations = [op for op in bulk_operations if op._filter['id'] != duplicate_id]
                    bulk_operations.append(UpdateOne({'id': duplicate_id}, {'$set': source_collection.find_one({'id': duplicate_id})}, upsert=True))
                    target_db[collection_name].bulk_write(bulk_operations)
                else:
                    raise
        except Exception as e:
            print(f"Error during synchronization for collection '{collection_name}': {e}") # Print the error details
            raise

from django.core.management.base import BaseCommand
from pymongo import MongoClient
import logging

class Command(BaseCommand):
    help = 'Synchronizes data between the main MongoDB and its replica.'

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
        exclude_collections = ['__schema__', 'django_migrations'] # Add any other collections to exclude
        for collection_name in source_db.list_collection_names():
            if collection_name in exclude_collections:
                continue # Skip the synchronization for excluded collections

            source_collection = source_db[collection_name]
            target_collection = target_db[collection_name]

            for source_document in source_collection.find():
                # Use 'id' for matching documents, assuming 'id' is the unique identifier
                document_id = source_document.get('id')
                if document_id is not None:
                    # Ensure '_id' is not included in the comparison
                    source_document.pop('_id', None)

                    # Check if a document with the same id already exists in the target collection
                    if target_collection.find_one({'id': document_id}):
                        # Document with the same id exists, skip the insertion or update
                        continue

                    # Check if a document with the same chatName already exists in the target collection
                    chatName = source_document.get('chatName')
                    if chatName and target_collection.find_one({'chatName': chatName}):
                        # Document with the same chatName exists, skip the insertion or update
                        continue

                    # Document does not exist in the target collection, insert it
                    target_collection.insert_one(source_document)
                else:
                    # Handle cases where 'id' is not present, if applicable
                    pass

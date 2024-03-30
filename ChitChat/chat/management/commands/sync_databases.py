from django.core.management.base import BaseCommand
from pymongo import MongoClient, UpdateOne, DeleteMany
from pymongo.errors import BulkWriteError
import logging
import hashlib
import datetime
import concurrent.futures

def run_synchronization():
    """
    Entry point function to run the synchronization process.
    It creates an instance of the Command class and calls its handle method.
    """
    command = Command()
    command.handle()

class Command(BaseCommand):
    help = 'Forcefully synchronizes data both databases.'

    def document_hash(self, document):
        """
        Calculates the hash of a document.
        It creates a copy of the document, removes the '_id' field, converts the document to a string,
        and calculates the SHA-256 hash of the string.

        Args:
            document (dict): The document to calculate the hash for.

        Returns:
            str: The SHA-256 hash of the document.
        """
        # Create a copy to avoid modifying the original document
        doc_copy = document.copy()
        doc_copy.pop('_id', None)
        # Convert the document to a string and hash it
        doc_string = str(doc_copy).encode('utf-8')
        return hashlib.sha256(doc_string).hexdigest()

    def handle(self, *args, **options):
        """
        The main method of the Command class.
        It connects to the main and replica databases, synchronizes data from main to replica,
        and optionally synchronizes data from replica to main.
        It handles exceptions and logs any errors that occur during the synchronization process.
        """
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
        """
        Synchronizes data between two databases.
        It retrieves the collection names to be synchronized based on the include and exclude lists.
        It uses a ThreadPoolExecutor to process each collection in parallel.

        Args:
            source_db (pymongo.database.Database): The source database.
            target_db (pymongo.database.Database): The target database.
        """
        include_collections = ['chat_message', 'chat_user']
        exclude_collections = ['__schema__', 'django_migrations']

        collection_names = [name for name in source_db.list_collection_names() if name in include_collections and name not in exclude_collections]

        # Using ThreadPoolExecutor to process collections in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(collection_names)) as executor:
            future_to_collection = {executor.submit(self.sync_collection, source_db, target_db, collection_name): collection_name for collection_name in collection_names}
            for future in concurrent.futures.as_completed(future_to_collection):
                collection_name = future_to_collection[future]
                try:
                    future.result()  # Wait for the collection to be processed
                except Exception as exc:
                    print(f"{collection_name} generated an exception: {exc}")

    def sync_collection(self, source_db, target_db, collection_name):
        """
        Synchronizes data for a specific collection between the source and target databases.
        It retrieves the latest 10,000 documents from the source collection, compares them with the target collection,
        and performs necessary update or insert operations using bulk write operations.
        It uses a MongoDB transaction to ensure data consistency.

        Args:
            source_db (pymongo.database.Database): The source database.
            target_db (pymongo.database.Database): The target database.
            collection_name (str): The name of the collection to synchronize.
        """
        print(f"Synchronizing collection: {collection_name}")
        source_collection = source_db[collection_name]
        target_collection = target_db[collection_name]

        batch_size = 1000
        last_id = None

        with target_db.client.start_session() as session:
            with session.start_transaction():
                while True:
                    # Sort by 'id' in descending order and limit to the latest 10,000 items
                    query = {} if last_id is None else {'id': {'$gt': last_id}}
                    source_documents = list(source_collection.find(query).sort('_id', -1).limit(10000))

                    if not source_documents:
                        break

                    bulk_operations = []

                    for source_document in source_documents:
                        document_id = source_document.get('id')
                        if document_id is not None:
                            source_document.pop('_id', None)

                            target_document = target_collection.find_one({'id': document_id}, session=session)
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

                    if bulk_operations:
                        try:
                            result = target_collection.bulk_write(bulk_operations, session=session)
                            print(f"Bulk operations result for collection '{collection_name}': {result.bulk_api_result}")
                        except BulkWriteError as e:
                            print(f"Error during bulk operations for collection '{collection_name}': {e}")
                            session.abort_transaction()
                            raise
                        except Exception as e:
                            print(f"Error during synchronization for collection '{collection_name}': {e}")
                            session.abort_transaction()
                            raise

                    # Since we're now working with a fixed set of the latest 10,000 items, break after processing them
                    break

                session.commit_transaction()

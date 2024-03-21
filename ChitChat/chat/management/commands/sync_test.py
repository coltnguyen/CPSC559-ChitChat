from django.core.management.base import BaseCommand
from pymongo import MongoClient, UpdateOne
import logging
import hashlib

class Command(BaseCommand):
    def synchronize_data():
        main_db_client = MongoClient('mongodb+srv://coltvnguyen:Legitpassword12@chitchat-cluster-1.gjvrsgz.mongodb.net/?retryWrites=true&w=majority')
        replica_db_client = MongoClient('mongodb+srv://coltvnguyen:Legitpassword12@chitchat-cluster-1.gjvrsgz.mongodb.net/?retryWrites=true&w=majority')
        main_db = main_db_client['chitchat_db']
        replica_db = replica_db_client['chitchat_db_replica']

        # Iterate over collections in the main database
        for collection_name in main_db.list_collection_names():
            main_collection = main_db[collection_name]
            replica_collection = replica_db[collection_name]

            # Retrieve documents from the main collection
            documents = main_collection.find()

            # Insert or update documents in the replica collection
            for document in documents:
                replica_collection.replace_one({'_id': document['_id']}, document, upsert=True)

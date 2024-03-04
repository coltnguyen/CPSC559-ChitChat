from pymongo import MongoClient
from pymongo.errors import PyMongoError


class ReplicaRouter:
    def db_for_read(self, model, **hints):
        """Directs read operations to the replica database, falling back to the default if the replica is not available."""
        try:
            # Attempt to connect to the default database
            if self.is_default_available():
                return 'default'
        except Exception:
            # If an error occurs (e.g., the default is down), fall back to the default
            pass
        return 'replica'

    def db_for_write(self, model, **hints):
        """Directs write operations to both the default and replica databases. This method should return a list of database aliases."""
        # FIX. Currently can only write to one database at a time.
        return 'replica'

    def is_default_available(self):
        """Checks if the default database is available for read operations."""
        # Configuration for connecting to the replica database
        default_config = {
            'host': 'mongodb+srv://coltvnguyen:Legitpassword12@chitchat-cluster-1.gjvrsgz.mongodb.net/?retryWrites=true&w=majority',
            'dbname': 'chitchat_db',
        }

        try:
            # Attempt to create a client and get database server status
            client = MongoClient(default_config['host'])
            db = client[default_config['dbname']]
            # Perform a simple operation like retrieving server status
            db.command("ping")
            return True
        except PyMongoError:
            # If any PyMongo error occurs, assume the replica is not available
            return False
        finally:
            # Close the client connection to clean up resources
            client.close()

    def allow_relation(self, obj1, obj2, **hints):
        """Allows any relation between two objects in the databases."""
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
      return True

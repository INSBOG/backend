import os
import pymongo
from numpy.f2py.auxfuncs import throw_error

from app.constants import logger

mongo_uri = os.getenv('MONGO_URL')
class Database:

    def __init__(self):
        try:
            self.conn = pymongo.MongoClient(mongo_uri, maxPoolSize=200)
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            raise Exception(e)

    def get_collection(self, collection):
        if self.conn:
            return self.conn.get_database('sddm')[collection]
        return None

    def close(self):
        if self.conn is not None:
            self.conn.close()
import json
import pymongo


class User:
    def __init__(self):
        client = pymongo.MongoClient()
        self.db = client['twitter_auction']
        self.collection = self.db['user_']

    def create_user(self, userdata):
        data = json.loads(userdata)
        user = self.collection.insert(data)
        return user

    def update_user(self, user_id, data):
        update = self.collection.update_one({'user_id': user_id}, data)
        return update

    def get_user(self, user_id):
        user = self.collection.find_one({'user_id': user_id})
        return user

    @staticmethod
    def filter_user():
        pass
import pymongo
from flask import json


class UserModel():
    def __init__(self, **kwargs):
        self.db = pymongo.MongoClient().twitter_auction

    def save_user(self, user_data):
        user_data = json.loads(user_data)
        return self.db.user.insert(user_data)

    def update_user(self, user_id):
        user = self.db.user.find_one({"user_id":user_id})
        return self.db.user.update_one({
                            "user_id": user_id},
                            {"user_id": user["user_id"] + 1}
                        )

    def count(self, user_id):
        return self.db.user.count({"user_id": user_id})


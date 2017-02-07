import json

import rabbit
from config import CONFIG
from elastic import Elastic


class UserTwitterModel:
    def __init__(self):
        self.db = Elastic()
        self.twitter_id = ""
        self.name = ""
        self.screen_name = ""
        self.profile_image = ""
        self.campaign = ""
        self.action = ""

    def push_to_queue(self):
        data = {
                "twitter_id": self.twitter_id, "name": self.name,
                "screen_name": self.screen_name,
                "profile_image": self.profile_image,
                "source": "twitter",
                "action": self.action}

        queue_name = (CONFIG.get('queue')).get('user_service')
        queue = rabbit.RabbitMQ(queue_name=queue_name)
        queue.producer(data=json.dumps(data))

    def save(self):
        data = {"twitter_id": self.twitter_id,
                 "name": self.name,
                "screen_name": self.screen_name,
                "profile_image": self.profile_image,
                "source": "twitter",
                "campaign": self.campaign,
                "action": self.action
                }
        self.db.insert('user', 'twitter_user', body=data)
        self.push_to_queue()
from datetime import datetime
import time
import tweepy
from flask import Flask
from delorean import Delorean
from flask import json
from flask import render_template
from flask import request

import tools
from response import Response
from config import CONFIG
from rabbit import RabbitMQ
from tweepy import OAuthHandler
from tweepy import Stream
import pymongo

app = Flask(__name__)

consumer_key = CONFIG.get('twitter').get('consumer_key')
consumer_secret = CONFIG.get('twitter').get('consumer_secret')
access_token = CONFIG.get('twitter').get('access_token')
access_token_secret = CONFIG.get('twitter').get('access_token_secret')


class CustomStreamListener(tweepy.StreamListener):
    def __init__(self, time_limit=None):
        self.start_time = time.time()
        self.limit = time_limit
        super(CustomStreamListener, self).__init__()

    def on_data(self, tweet_data):
        queue_name = (CONFIG.get('queue')).get('twitter')
        rabbit = RabbitMQ(queue_name)
        if (time.time() - self.start_time) < self.limit:
            print tweet_data
            rabbit.producer(tweet_data)
            return True
        else:
            rabbit.consumer()
            return False

    def on_error(self, status_code):
        return True

    def on_timeout(self):
        return True


def startStream(hashtag, end):
    twitter_config = CONFIG.get('twitter')
    auth = OAuthHandler(twitter_config.get('consumer_api_key'), twitter_config.get('consumer_api_secret'))
    auth.set_access_token(twitter_config.get('access_token'), twitter_config.get('access_token_secret'))
    auctionStream = Stream(auth, CustomStreamListener(end))
    auctionStream.filter(track=hashtag)


@app.route('/')
def index():
    users = []
    context = pymongo.MongoClient().twitterauction.users.find({})
    for doc in context:
        users.append(doc)
        print users
    return render_template('hello.html', users=users)


@app.route('/listen', methods=['POST'])
def listen():
    request_data = dict(request.form)

    hashtag = request_data['hashtag']
    starthour, startminute = ''.join(request_data['startTime']).split(':')
    hour, minute = ''.join(request_data['duration']).split(':')

    now = datetime.now()

    if now.hour == int(starthour):
        print "Here"
        print now.minute, startminute
        if now.minute <= int(startminute):
            print "He"
            # time.sleep((int(startminute) - now.minute) * 60)
            startStream(hashtag, tools.to_sec("{0}:{1}:1".format(hour, minute, 0)))
        else:
            message = {
                "hashtag": hashtag,
                "starttime": "{0}:{1}".format(starthour, startminute),
                "Duration": "{0} seconds".format(tools.to_sec("{0}:{1}:1".format(hour, minute, 0))
                                                 )}
            error = {"message": "Unable to listen to twitter stream at "
                                "the provided time",
                     "reason": "Start time has passed"
                     }
            return Response.response_error(message, error)

    elif now.hour > int(starthour):
            message = {
                "hashtag": hashtag,
                "starttime": "{0}:{1}".format(starthour, startminute),
                "Duration": "{0} seconds".format(tools.to_sec("{0}:{1}:1".format(hour, minute, 0))
                                                 )}
            error = {"message": "Unable to listen to twitter stream at "
                                "the provided time",
                     "reason": "Start time has passed"
                     }
            return Response.response_error(message, error)
    else:
        print "Okay"
        if now.hour < int(starthour):
            if now.minute <= int(startminute):
                # time.sleep((int(startminute) - now.minute) * 60)
                startStream(hashtag, tools.to_sec("{0}:{1}:1".format(hour, minute, 0)))
            elif now.minute > int(startminute):
                message = {
                    "hashtag": hashtag,
                    "starttime": "{0}:{1}".format(starthour, startminute),
                    "Duration": "{0} seconds".format(tools.to_sec("{0}:{1}:1".format(hour, minute, 0))
                                                     )}
                error = {"message": "Unable to listen to twitter stream at "
                                    "the provided time",
                         "reason": "Start time has passed"
                         }
                return Response.response_error(message, error)


if __name__ == '__main__':
    app.run(port=2000, debug=True)

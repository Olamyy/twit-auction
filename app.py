from __future__ import unicode_literals
from __future__ import absolute_import, print_function
import pymongo
import time
import tweepy
import flask_api
from flask import request
import config

app = flask_api.FlaskAPI(__name__)
from tweepy.streaming import json
from tweepy import OAuthHandler
from tweepy import Stream

consumer_key = config.CONFIG.get('twitter').get('consumer_key')
consumer_secret = config.CONFIG.get('twitter').get('consumer_secret')
access_token = config.CONFIG.get('twitter').get('access_token')
access_token_secret = config.CONFIG.get('twitter').get('access_token_secret')


class CustomStreamListener(tweepy.StreamListener):
    def __init__(self, duration=None):
        super(CustomStreamListener, self).__init__()
        self.duration = duration
        super(tweepy.StreamListener, self).__init__()

        self.db = pymongo.MongoClient().test

    def on_data(self, tweet):
        print(json.loads(tweet)['entities'])
        endtime = time.time() + float(self.duration)
        while time.time() < endtime:
            self.filter_stream(json.loads(tweet))

    def on_error(self, status_code):
        return True

    def on_timeout(self):
        return True

    def filter_stream(self, param):
        pass


def startStream(hashtag, duration):
    twitter_config = config.CONFIG.get('twitter')
    auth = OAuthHandler(twitter_config.get('consumer_api_key'), twitter_config.get('consumer_api_secret'))
    auth.set_access_token(twitter_config.get('access_token'), twitter_config.get('access_token_secret'))
    auctionStream = Stream(auth, CustomStreamListener(duration))
    auctionStream.filter(track=hashtag)


@app.route('/listen', methods=['POST'])
def listen():
    hashtag = request.data['hashtag']
    time = request.data['time']
    data = "Listening for {0} seconds for {1}".format(time, hashtag)
    response = {'status': 'success', 'data': data}
    startStream(hashtag, duration=time)
    return response


if __name__ == '__main__':
    app.run()

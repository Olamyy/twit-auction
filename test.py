from datetime import datetime
import time

import pymongo
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

app = Flask(__name__)

consumer_key = CONFIG.get('twitter').get('consumer_key')
consumer_secret = CONFIG.get('twitter').get('consumer_secret')
access_token = CONFIG.get('twitter').get('access_token')
access_token_secret = CONFIG.get('twitter').get('access_token_secret')


class CustomStreamListener(tweepy.StreamListener):
    def __init__(self, api):
        super(CustomStreamListener, self).__init__(api)
        self.api = api

        self.db = pymongo.MongoClient().test

    def on_data(self, tweet):
        print(json.loads(tweet))
        self.db.tweets.insert(json.loads(tweet))

    def on_error(self, status_code):
        return True  # Don't kill the stream

    def on_timeout(self):
        return True  # Don't kill the stream


def startStream(hashtag, end):
    twitter_config = CONFIG.get('twitter')
    auth = OAuthHandler(twitter_config.get('consumer_api_key'), twitter_config.get('consumer_api_secret'))
    auth.set_access_token(twitter_config.get('access_token'), twitter_config.get('access_token_secret'))
    auctionStream = Stream(auth, CustomStreamListener(end))
    auctionStream.filter(track=hashtag)


startStream("IStandWithNigeria", 0)
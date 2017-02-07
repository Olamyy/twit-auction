from datetime import datetime
import time
import tweepy
import flask_api
import os
from flask import Flask
from delorean import Delorean
from flask import json
from flask import render_template
from flask import request

import tools
from response import Response
from config import CONFIG
import rabbit
from tweepy import OAuthHandler
from tweepy import Stream

app = Flask(__name__)

consumer_key = CONFIG.get('twitter').get('consumer_key')
consumer_secret = CONFIG.get('twitter').get('consumer_secret')
access_token = CONFIG.get('twitter').get('access_token')
access_token_secret = CONFIG.get('twitter').get('access_token_secret')


class CustomStreamListener(tweepy.StreamListener):
    def __init__(self, end):
        super(CustomStreamListener, self).__init__()
        self.duration = int(end)
        super(tweepy.StreamListener, self).__init__()

    def check(self, tweet_data):
        queue_name = (CONFIG.get('queue')).get('twitter')
        startTime = time.time()
        print self.duration
        duration = self.duration
        while True:
            # queue = rabbit.RabbitMQ(queue_name)
            # queue.producer(tweet_data)
            print "Received Tweet"
            if time.time() > startTime + duration:
                break
            print('Done')

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
    return render_template('hello.html', name="Test")


@app.route('/listen', methods=['POST'])
def listen():
    request_data = dict(request.form)

    hashtag = request_data['hashtag']
    starthour, startminute = ''.join(request_data['startTime']).split(':')
    endhour, endminute = ''.join(request_data['endTime']).split(':')

    now = datetime.now()

    if now.hour > int(starthour):
        message = {
            "hashtag": hashtag,
            "starttime": "{0}:{1}".format(starthour, startminute),
            "endTime": "{0}:{1}".format(endhour, endminute)
        }
        error = {"message": "Unable to listen to twitter stream at "
                            "the provided time",
                 "reason": "Start time has passed"
                 }
        return Response.response_error(message, error)
    else:
        if now.hour < int(starthour):
            data = {
                "hashtag": hashtag,
                "startTime": "{0}:{1}".format(starthour, startminute),
                "endTime": "{0}:{1}".format(endhour, endminute),
                "message": "Streaming would begin by {0}:{1}".format(starthour, startminute)
            }
            time.sleep(int(1))
            startStream(hashtag, tools.to_sec("{0}:{1}:{0}".format(endhour, endminute, 1)))
        else:
            end_time = tools.to_sec("{0}:{1}:{1}".format(endhour, endminute, 0))
            startStream(hashtag, end_time)


if __name__ == '__main__':
    app.run(port=2000, debug=True)

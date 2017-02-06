from datetime import datetime
import time
import tweepy
import flask_api
from delorean import Delorean
from flask import request

from response import Response
from config import CONFIG
from lib.rabbit import RabbitMQ
from tweepy import OAuthHandler
from tweepy import Stream

app = flask_api.FlaskAPI(__name__)

consumer_key = CONFIG.get('twitter').get('consumer_key')
consumer_secret = CONFIG.get('twitter').get('consumer_secret')
access_token = CONFIG.get('twitter').get('access_token')
access_token_secret = CONFIG.get('twitter').get('access_token_secret')


class CustomStreamListener(tweepy.StreamListener):
    def __init__(self, duration=None):
        super(CustomStreamListener, self).__init__()
        self.duration = duration
        super(tweepy.StreamListener, self).__init__()

    def on_data(self, tweet_data):
        queue_name = (CONFIG.get('queue')).get('twitter')
        startTime = time.time()
        endTime = time.time() + int(60 * self.duration)
        while True:
            rabbit = RabbitMQ(queue_name)
            rabbit.producer(tweet_data)
            print "Received Tweet"
            if time.time() > endTime:
                break
        print('Took %s seconds to calculate.' % (endTime - startTime))

    def on_error(self, status_code):
        return True

    def on_timeout(self):
        return True


def startStream(hashtag, **kwargs):
    twitter_config = CONFIG.get('twitter')
    auth = OAuthHandler(twitter_config.get('consumer_api_key'), twitter_config.get('consumer_api_secret'))
    auth.set_access_token(twitter_config.get('access_token'), twitter_config.get('access_token_secret'))
    auctionStream = Stream(auth, CustomStreamListener(**kwargs))
    auctionStream.filter(track=hashtag)


@app.route('/listen', methods=['POST'])
def listen():
    hashtag = request.data['hashtag']
    starthour, startminute = request.data['startTime'].split(':')
    endhour, endminute = request.data['endTime'].split(':')

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
        data = {
            "hashtag": hashtag,
            "startTime": "{0}:{1}".format(starthour, startminute),
            "endTime": "{0}:{1}".format(endhour, endminute),
            "message": "Streaming would begin by {0}:{1}".format(starthour, startminute)
        }
        startStream(hashtag, starthour=starthour, startminute=startminute, endhour=endhour, endminute=endminute)


if __name__ == '__main__':
    app.run(port=2000)

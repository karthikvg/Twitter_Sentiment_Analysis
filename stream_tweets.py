from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import Stream
from tweepy import OAuthHandler
from textblob import TextBlob

import re
import numpy as np
import pandas as pd
import credits
import matplotlib.pyplot as plt
import helpers


class TwitterClient:
    def __init__(self, user=None):  # Authenticates the user
        self.auth = TwitterAuthenticator().authenticate()
        self.twitter_client = API(self.auth, wait_on_rate_limit=True)
        self.user = user

    def get_timeline_tweets(self, count):  # Generates the timeline tweets for a given user id
        tweets = list()
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.user).items(count):
            tweets.append(tweet)
        return tweets

    def get_friends(self, count):  # Returns all the friends for a given user id
        friends = list()
        for friend in Cursor(self.twitter_client.friends, id=self.user).items(count):
            friends.append(friend)
        return friends

    def get_twitter_client_api(self):  # Return the the twitter_client_api of the authenticated user
        return self.twitter_client


# TwitterListener is used to get the data and also to handle the errors
class TwitterListener(StreamListener):

    def __init__(self, filename):
        self.filename = filename

    def on_data(self, data):
        with open(self.filename, 'a')as writing:
            writing.write(data)
        return True

    def on_error(self, status):
        if status == 420:
            print(status)
            return False
        print(status)


# TwitterAuthenticator is used to authenticate the user with credentials listed in credits.py
class TwitterAuthenticator:

    def authenticate(self):  # A method to authenticate the user
        auth = OAuthHandler(credits.CONSUMER_KEY, credits.CONSUMER_SECRET)
        auth.set_access_token(credits.ACCESS_TOKEN, credits.ACCESS_SECRET)
        return auth


class TwitterStreamer:

    def __init__(self):
        self.auth = TwitterAuthenticator()

    def stream_tweets(self, filename,
                      hash_tag_list):  # Used to stream tweets for the given hash_tag_list to given file name

        listener = TwitterListener(filename)
        auth = self.auth.authenticate()
        stream = Stream(auth, listener)
        stream.filter(track=hash_tag_list)


class TweetAnalyzer:

    def clean_tweet(self, tweet):  # Used to clean the given tweet which makes use of regular expression library
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyze_tweet_sentiment(self, tweet):  # Returns 1,-1,0 for positive, negative, neutral sentiments respectively
        analyze = TextBlob(self.clean_tweet(tweet))
        if analyze.sentiment.polarity > 0:
            return 1
        elif analyze.sentiment.polarity < 0:
            return -1
        else:
            return 0

    def tweets_to_data_frame(self, tweets):  # Returns a data_frame of a tweets with required fields
        dataFrame = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=["tweets"])
        dataFrame['Source'] = np.array([tweet.source for tweet in tweets])
        dataFrame['date'] = np.array([tweet.created_at for tweet in tweets])
        dataFrame['len'] = np.array([len(tweet.text) for tweet in tweets])
        dataFrame['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        return dataFrame


if __name__ == "__main__":
    user = TwitterClient()
    api = user.get_twitter_client_api()
    tweets = api.user_timeline(screen_name='MelissaBenoist', count=200)
    analyzer_temp = TweetAnalyzer()
    data_frame = analyzer_temp.tweets_to_data_frame(tweets)
    data_frame['Sentiment'] = np.array([analyzer_temp.analyze_tweet_sentiment(tweet) for tweet in data_frame['tweets']])
    print(data_frame)

    ################################
    # print(dir(tweets[0]))
    # print(data_frame.head(5))
    # print(data_frame['likes'])
    # print(dir(tweets[0]))
    # print(np.max(data_frame['likes']))
    # time_likes = pd.Series(data=data_frame['len'].values*100, index=data_frame['date'])
    # time_likes.plot(figsize=(16, 4), label='len', legend=True)
    # time_likes = pd.Series(data=data_frame['likes'].values, index=data_frame['date'])
    # time_likes.plot(figsize=(16, 4), label='likes', legend=True)
    # plt.show()

    ######################################
    # filename="karthik.json"
    # hash_tag_list=["teradata"]
    # tweets=user.get_timeline_tweets(0)
    # friends=user.get_friends(0)
    # print("the no of tweets for the given account id",len(tweets),sep="   ")
    # print("the no of friends for the given account id",len(friends),sep="   ")
    # for friend in friends:
    #    print(friend)
    # helpers.write_to_a_file("tweets.json",tweets)
    # helpers.write_to_a_file("friends.txt",friends)
    # stream_tweets=TwitterStreamer()
    # stream_tweets.stream_tweets(filename,hash_tag_list)

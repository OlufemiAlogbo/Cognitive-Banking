#!/usr/bin/env python
from flask import Flask, render_template
import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
import numpy as np

class TwitterClient(object):
    '''
    Generic Twitter Class for sentiment analysis.
    '''
    def __init__(self):
        '''
        Class constructor or initialization method.
        '''
        # keys and tokens from the Twitter Dev Console
        consumer_key = 'DfIy1C6nWTRRPmPp9T2RgTAHm'
        consumer_secret = 'huTNpYD07VjeHinBygFMbTiCfOwg8PRlOVKGWXDF5NIiRT7ek1'
        access_token = '197442507-L2dg0LzGslDwIqNAuVR2UNKlgk4u9yFxMvwVHJ0v'
        access_token_secret = 'cPSPB1Yv3pVBFY2Av68ctSjPWFp6FMzvf6PtXA5oTbSxr'

        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z])|(\w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    def get_tweets(self, query, count = 10):
        '''
        Main function to fetch tweets and parse them.
        '''
        # empty list to store parsed tweets
        tweets = []

        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.api.search(q = query, count = count)

            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                parsed_tweet = {}

                # saving text of tweet
                parsed_tweet['text'] = tweet.text
                # saving sentiment of tweet
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)

                # appending parsed tweet to tweets list
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)

            # return parsed tweets
            return tweets

        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))


app = Flask(__name__)

@app.route("/")
def hello():
    # creating object of TwitterClient Class
    api = TwitterClient()
    # calling function to get tweets
    tweets = api.get_tweets(query = '@unionbank_ng', count = 1000)
    # picking positive tweets from tweets
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']

    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']

    Stat = [format(100*len(ptweets)/len(tweets)), format(100*len(ntweets)/len(tweets)), format(100*(len(tweets) - len(ntweets) - len(ptweets))/len(tweets))]

    return render_template("index.html", Stat = Stat, tweets = tweets, ptweets = ptweets, ntweets = ntweets)

if __name__ == "__main__":
    app.run()

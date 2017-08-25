#!/usr/bin/env python3


import tweepy
import time
import sys
import re
import csv

# import authentication data
# in separate file to keep secret key secret
from authentication_data import *

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)
api = tweepy.API(auth)

if not api:
    print("Error connecting to API!")



#Inherit from the StreamListener object
class MyStreamListener(tweepy.StreamListener):

    #Overload the on_status method
    def on_status(self, status):
        try:

            #Check if the tweet has coordinates, if so write it to text
            if (status.coordinates is not None and status.source == 'Instagram' and status.lang == 'en'):
                print("Found insta:", status.text)
            return True

        #Error handling
        except BaseException as e:
            print("Error on_status: %s" % str(e))
        return True

    #Error handling
    def on_error(self, status):
        print(status)
        return True

    #Timeout handling
    def on_timeout(self):
        print('timeout')
        return True 

#Create a stream object  
twitter_stream = tweepy.Stream(auth, MyStreamListener())
#twitter_stream.filter(languages='en')
#twitter_stream.filter(track=['vacation'])
twitter_stream.filter(locations=[-180,-90,180,90])



# open CSV
#timestr = time.strftime("%Y%m%d-%H%M%S")
#tweetcsv = 'tweet_data_' + timestr  + '.csv'
#with open(tweetcsv, 'w', encoding='utf-8', newline='') as csvfile:
#    spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)

    # read tweets
#    max_tweets = 10000000
#    tweetcount = 0
#    goodtweetcount = 0
#    query = "travel OR vacation OR trip OR vacay OR holiday OR getaway AND source:Instagram lang:en"
#    for status in tweepy.Cursor(api.search, q=query).items(max_tweets):
#        tweetcount += 1

        # only get tweets with location data and from instagram
#        if status.coordinates and status.source=='Instagram':
#            latitude = status.coordinates['coordinates'][1]
#            longitude = status.coordinates['coordinates'][0]

#            tweet_text = ' '.join(status.text.split())
#            regex = re.search("^(.*) (https://[\w./]+)$", tweet_text)
#            if regex:
#                content = regex.group(1)
#                url = regex.group(2)
#                spamwriter.writerow([status.id, status.user.screen_name, latitude, longitude, url, content])
#                goodtweetcount += 1
#            else:
#                print("Could not read", tweet_text)

#    print("read", goodtweetcount, "out of", tweetcount, "tweets")
#    print(api.rate_limit_status()['resources']['search'])




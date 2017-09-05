#!/usr/bin/env python3


import tweepy
import time
import sys
import os
import re
import csv
from bs4 import BeautifulSoup
import requests
import json
from urllib3.exceptions import ProtocolError

# import authentication data
# in separate file to keep secret key secret
from authentication_data import *

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)
api = tweepy.API(auth)

if not api:
    print("Error connecting to API!")


## write to files
timestr = time.strftime("%Y%m%d-%H%M%S")
tweetcsv = os.path.join('CSVs', 'tweet_data_' + timestr  + '.csv')
tweetf = open(tweetcsv, 'w', encoding='utf-8', newline='')
tweetwriter = csv.writer(tweetf, quoting=csv.QUOTE_MINIMAL)
instacsv = os.path.join('CSVs', 'instagram_data_' + timestr  + '.csv')
instaf = open(instacsv, 'w', encoding='utf-8', newline='')
instawriter = csv.writer(instaf, quoting=csv.QUOTE_MINIMAL)


def applySoup(page, url):
    # parse with beautiful soup
    soup = BeautifulSoup(page.text, 'html.parser')
    scripts = soup.select('script')
    for script in scripts:
        # find area with javascript
        if re.match('window._sharedData = ', script.text):
            try:
                data = json.loads(script.contents[0][21:-1])
            except ValueError as e:
                return( ('error', url, 'json loading', e) )
            else:
                try:
                    rawcaption = str(data["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["edge_media_to_caption"]["edges"][0]["node"]["text"])
                except KeyError as e:
                    return( ('error', url, 'json parsing', e) )
                else:
                    caption = ' '.join(rawcaption.split())
                    return( ('caption', url, caption) )
    return( ('error', url, 'Soup', None) )

def retrieveURL(url):
    try:
        instagram_page = requests.get(url)
    except requests.exceptions.HTTPError as e:
        return( ('error', None, 'HTTP', e) )
    except KeyboardInterrupt:
        raise Exception('Keyboard interruption')
    else:
        soup_result = applySoup(instagram_page, url)
        return(soup_result)



def getInstagramData(tweetid, url):
    # retrieve instagram page
    soup_result = retrieveURL(url)
    if soup_result[0] == 'caption':
        # write CSV
        instawriter.writerow( [tweetid, soup_result[1], soup_result[2]] )
        print(soup_result[1], soup_result[2])




def process_status(status):
    latitude = status.coordinates['coordinates'][1]
    longitude = status.coordinates['coordinates'][0]

    tweet_text = ' '.join(status.text.split())
    regex = re.search("^(.*) (https://[\w./]+)$", tweet_text)
    if regex:
        content = regex.group(1)
        url = regex.group(2)
        tweetwriter.writerow([status.id, status.user.screen_name, latitude, longitude, url, content, status.created_at])

        getInstagramData(status.id, url)
    else:
        print("Could not read", tweet_text)



#Inherit from the StreamListener object
class MyStreamListener(tweepy.StreamListener):

    #Overload the on_status method
    def on_status(self, status):
        try:

            #Check if the tweet has coordinates, if so write it to text
            if (status.coordinates is not None and status.source == 'Instagram' and status.lang == 'en'):
                process_status(status)
            return True

        #Error handling
        except BaseException as e:
            print("Error on_status: %s %s %s" % (str(e), status.user.screen_name, status.id))
        except KeyboardInterrupt:
            raise Exception('Keyboard interruption')
            return False
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
while True:
    try:
        twitter_stream = tweepy.Stream(auth, MyStreamListener())
        twitter_stream.filter(locations=[-180,-90,180,90])
    except ProtocolError:
        continue
    except KeyboardInterrupt:
        twitter_stream.disconnect()
        break



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




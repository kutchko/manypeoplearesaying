#!/usr/bin/env python3


import time
import os
import csv
import re
import pymysql.cursors
from bs4 import BeautifulSoup
import requests
import json


user = 'kkutchko'
passwd = 'password'
database = 'vacation'

connection = pymysql.connect(host='localhost',
    user=user,
    password=passwd,
    db=database,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor)

timestr = time.strftime("%Y%m%d-%H%M%S")
instacsv = os.path.join('instagram_CSV', 'instagram_data_' + timestr  + '.csv')

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
    else:
        soup_result = applySoup(instagram_page, url)
        return(soup_result)

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT handle, id, url FROM tweets WHERE instagram = 'N' LIMIT 5")


        with open(instacsv, 'w', encoding='utf-8', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)

            # create mechanism to check if there are more than 10 errors in a row
            errorCount = 0

            for row in cursor:
                # retrieve instagram page
                url = row['url'].strip("'")
                soup_result = retrieveURL(url)
                if soup_result[0] == 'caption':
                    # write CSV
                    spamwriter.writerow( [row['id'], soup_result[1], soup_result[2], None, None, instacsv] )

                    # mark table

                    errorCount = 0
                else:
                    # write CSV
                    errorCount += 1
                    spamwriter.writerow( [row['id'], soup_result[1], None, soup_result[2], soup_result[3], instacsv] )

                    # mark table

                    # too many errors in a row?
                    if errorCount > 10:
                        raise RuntimeError('Too many errors in a row!') from soup_result[3]

                time.sleep(0.5)
finally:
    connection.commit()
    connection.close()






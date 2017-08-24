#!/usr/bin/env python3



import csv
import pymysql.cursors



user = 'kkutchko'
passwd = 'password'
database = 'vacation'

csvfiles = ['tweet_data.csv']


connection = pymysql.connect(host='localhost',
    user=user,
    password=passwd,
    db=database,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor)


try:
    with connection.cursor() as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS tweets (" +\
                "id BIGINT(18) NOT NULL, " +\
                "handle VARCHAR(17), " +\
                "longitude DECIMAL(11, 8), " +\
                "latitude DECIMAL(11, 8), " +\
                "url VARCHAR(25), " +\
                "tweet VARCHAR(119), " +\
                "instagram CHAR(1) DEFAULT 'N', " +\
                "PRIMARY KEY (id)) CHARACTER SET utf8mb4")

        for csvfile in csvfiles:
            with open(csvfile, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                
                for row in reader:
                    try:
                        cursor.execute('INSERT INTO tweets ' +\
                            '(id, handle, longitude, latitude, url, tweet) ' +\
                            'VALUES (%s, "%s", %s, %s, "%s", "%s") ' +\
                            'ON DUPLICATE KEY UPDATE id=id',
                            row)
                    except pymysql.err.InternalError as e:
                        print ("MySQL Error [%d]: %s for tweet %s" % (e.args[0], e.args[1], row[0]))
                    except pymysql.err.DataError as e:
                        print ("MySQL Error [%d]: %s for tweet %s" % (e.args[0], e.args[1], row[0]))
finally:
    connection.commit()
    connection.close()




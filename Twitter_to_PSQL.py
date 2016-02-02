import psycopg2
from psycopg2.extensions import AsIs
import sys, os
import json
import numpy as np

def TweetCollectionPSQL(inputfile,databasename,tablename):
    #INPUT:
    #   inputfile: File name of the JSON output from Twitter API streamer.
    #   databasename: The PSQL database name that Twitter data should be saved to.
    #   tablename: Table name within the PSQL database that Twitter data should
    #              be saved to.
    #              Table created using the example command:
    #                   CREATE TABLE tweets (
    #                   tid character varying NOT NULL,
    #                   data json);
    #OUTPUT:
    #   Data will be inserted into the PSQL database.
    #EXAMPLE CALL:
    #   Start the psql server before loading python:
    #   > /etc/init.d/postgresql start 
    #   > inputfile = 'davidbowietributes0.json'
    #   > TweetCollection(inputfile, 'testdb', 'tweets')
    #REFERENCES:
    #   Base code tutorial: http://zetcode.com/db/postgresqlpythontutorial/

    twitterdata = []
    with open(inputfile) as file:
        for line in file:
            twitterdata.append(json.loads(line))

    try:
        con = None
        con = psycopg2.connect(database=databasename)
        cur = con.cursor()
        #We want to save the id and the JSON dictionary from the Twitter API.
        psql_command = "INSERT INTO "+str(tablename)+" (tid, data) VALUES (%s, %s)"
        numrows = np.array(xrange(len(twitterdata)))
        map(lambda x: cur.execute(psql_command, (twitterdata[x]['id'],json.dumps(twitterdata[x]))), numrows)
        con.commit()

    except psycopg2.DatabaseError, e:
        if con:
            con.rollback()

        print 'Error %s' % e    
        sys.exit(1)

    finally:
        if con:
            cur.close()
            con.close()
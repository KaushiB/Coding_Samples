# Coding_Samples

Python script samples.

1) A visualization of of YELP ratings of Ottawa restaurants. The YELP search API was integrated into a Python script to search for restaurant information in Ottawa and the surrounding suburban areas. The YELP search API only returns the 40 top results (from a given sort order) for regular developers. To mitigate this restriction, the complete geographical area was split into a grid of uniform length in kilometers (Note: this does not equal to uniform angular distance), using the Haversine formula to compute the coordinates of the vertices. If each cell in the grid contained more than 20 results (the initial output is only of the 20 top results out of 40, you can use "offset" parameter in the API call to get the rest), that cell was sampled at a finer interval to get < 20 results (this is important if a cell has > 40 results, which is the case in dense urban areas). The resulting output was cleaned to make a .csv file that contained the restaurant name, city/suburb, latitude, longitude, address, phone, YELP rating, vote count, category and YELP URL. Please note that only restaurants that has a vote count > 0 are used in the visualization. The visualization was done using Tableau Public. The relevant Python code(s) used for this exercise were:

makeAgrid.py
yelpapicall.py
yelpcleanup.py

*******************************************************************************************************
!!!UPDATE!!!: I have added several extra coding samples labeled *OOP.py which attains the same objectives as makeAgrid.py and yelpapicall.py. With the newer coding samples, I'm adopting an Object-Oriented Programming style (and improving as fast as possible!) as opposed to procedural style programming, which I'm told is a quick give-away of people coming from an academic background. The code yelprestaurantsearch.py calls on the Classes and their corresponding instances to create a dataframe which contains the YELP information about restaurants in Ottawa. These codes can be adapted to search for any type of businesses in any city with the YELP search API by changing the geographical input, "search_term" and "search_type" parameters.
********************************************************************************************************

The visualization can be viewed at:

https://public.tableau.com/profile/kaushala.bandara#!/vizhome/YELP_ratings_Ottawa_modified/YELP_dashboard2

2) A word cloud containing the most common words in the Twitter tributes to David Bowie in the aftermath of his death. Approximately 1.5 million tweets, which referenced #DavidBowie or #RIPDavidBowie, were streamed using the Twitter API in Python (the Twitter API streamer was stopped at 1.5 million tweets due to network issues). Tweets from the resulting JSON files were converted into a .csv file that contained the text of each tweet and its corresponding language. The tweets were then filtered to only reflect the English language (not including common stopwords in the english language, url references, twitter handles, retweet tags and placeholders for empty text). The word cloud was then constructed using the most common words that appear in the tweets, in the shape of Twitter logo. The 70's style font was specifically installed for the visualization purpose of this cloud. The relevant Python code(s) used for this exercise were:

TweetViz.py
* The Twitter API Python streamer from http://marcobonzanini.com/2015/03/02/mining-twitter-data-with-python-part-1/ is not included here.

The visualization is included in this repository: davidbowietributes.png

3) File added on February 2, 2016. A simple code to take the JSON output from the Twitter API streaming code and store the data in a PostgreSQL database. Store a few tables for more SQL authoring exercises.

Twitter_to_PSQL.py
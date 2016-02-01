import json
import pandas as pd
import numpy as np
import unicodedata
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from scipy.misc import imread
import sys, os

#REFERENCES: Twitter data was streamed using the base code in:
#            http://marcobonzanini.com/2015/03/02/mining-twitter-data-with-python-part-1/
#            Streaming done for specific hastag(s).
#            For example, #DavidBowie or #RIPDavidBowie
#            Reference for word cloud:
#            https://amueller.github.io/word_cloud/index.html


def TweetCollection(inputlist,outputfile):
    #INPUT:
    #   inputlist: An array of file names that contains the output from twitter streamer.
    #              There maybe multiple files if the twitter stream fails in the middle, due to network issues.
    #OUTPUT:
    #   mastertwitterdf : A combined dataframe with information about all tweets.
    #   outputfile: A file that contains a dataframe with the text of each tweet and language.
    #               This file could also contain other info, depending on your visualization needs.
    #               If so, modify this function to include other keys from JSON dictionary from twitter API output.
    #EXAMPLE CALL:
    #   inputfiles = ['davidbowietributes0.json','davidbowietributes1.json',...]
    #   df = TweetCollection(inputfiles,'example_output.csv')
    #
    os.chdir('/home/kaushi/Desktop/Python_programming/Twitter/')
    colnames = ['text','language']
    mastertwitterdf = pd.DataFrame(columns=colnames)
    
    for i in range(len(inputlist)):
        dataread = []
        with open(inputlist[i]) as file:
            for line in file:
                dataread.append(json.loads(line))
    
        temptweets = pd.DataFrame(columns=colnames)
    
        numrows = np.array(xrange(len(dataread)))
        temptweets['text'] = map(lambda x: dataread[x]['text'] if dataread[x].has_key('text') else None, numrows)
        temptweets['language'] = map(lambda x: dataread[x]['lang'] if dataread[x].has_key('lang') else None, numrows)
    
        mastertwitterdf = pd.concat([mastertwitterdf,temptweets], ignore_index=True)
    
    mastertwitterdf = mastertwitterdf[mastertwitterdf['language'].notnull()]
    mastertwitterdf.reset_index(drop=True)
    mastertwitterdf.to_csv(outputfile,sep=',',encoding='utf-8')
    
    return mastertwitterdf

def TweetWordCloud(inputfile,lang,outputimage):
    #INPUT:
    #   inputfile: A csv (or other format) file with a collection of tweet text and language information.
    #   lang: The target language of the word cloud.
    #         (Use the twitter codes, such as 'en' for English 'fr' for French etc.)
    #OUTPUT:
    #   outputimage: A png file with the word cloud image.
    #EXAMPLE CALL:
    #   TweetWordCloud('DavidBowieTributes.csv','en', 'davidbowietributes.png')
    #
    os.chdir('/home/kaushi/Desktop/Python_programming/Twitter/')
    colnames = ['text','language']
    tweetdf = pd.read_csv(inputfile,header=0,names=colnames)
    tweetdf['text'] = tweetdf['text'].astype(str)
    
    tweetdf2 = tweetdf[tweetdf['language'] == lang] #Only select the English tweets, for example.
    tweetdf2.reset_index(drop=True) #--> Reset indices, otherwise further manipulations will encounter issues.
    
    #Construct the word cloud.
    words = ' '.join(tweetdf2['text'])
    wordfilter = " ".join([word for word in words.split()
                           if 'http' not in word #Take out urls
                           and not word.startswith('@') #Take out twitter handles.
                           and word != 'RT' #Take out retweet tags.
                           and word != 'None' #Take out place holders and null values.
                           and word != 'nan'])
    
    #Download the twitter mask (or any other mask of preference.)
    twitter_mask = imread('twitter_mask.png', flatten=True)
    wordcloud = WordCloud(font_path='/home/kaushi/customfonts/actionis.ttf', stopwords=STOPWORDS.add("will"),\
                          background_color='black',width=3000, height=3000,min_font_size=8,\
                          relative_scaling=0.3,mask=twitter_mask).generate(wordfilter)
    
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.savefig(outputimage, dpi=1000)
    plt.show()
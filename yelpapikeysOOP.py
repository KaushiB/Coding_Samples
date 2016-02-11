import numpy as np
import pandas as pd
import sys, os
import json

class YelpKeys(object):

	def __init__(self,yelpresultsdict=None):
		#yelpresultsdict = Python dictionary that stores results of the YELP search API.
		self.yelpresultsdict = yelpresultsdict

	def create_listings(self):
		#Results dictionary only stores 20 results or less at a time.
		if (self.yelpresultsdict['total'] < 20):
			return np.array(xrange(self.yelpresultsdict['total']))
		else:
			return np.array(xrange(20))

	def name(self):
		Name = map(lambda x: \
			   self.yelpresultsdict["businesses"][x]['name'] if \
		       self.yelpresultsdict["businesses"][x].has_key('name') else None, \
		       self.create_listings())
		return Name

	def city(self):
		City = map(lambda x: \
			   self.yelpresultsdict["businesses"][x]['location']['city'] if \
			   self.yelpresultsdict["businesses"][x]['location'].has_key('city') else None, \
			   self.create_listings())
		return City

	def latitude(self):
		Latitude = map(lambda x: \
				   self.yelpresultsdict["businesses"][x]['location']['coordinate']['latitude'] if \
				   self.yelpresultsdict["businesses"][x]['location'].has_key('coordinate') else None, \
				   self.create_listings())
		return Latitude

	def longitude(self):
		Longitude = map(lambda x: \
					self.yelpresultsdict["businesses"][x]['location']['coordinate']['longitude'] if \
					self.yelpresultsdict["businesses"][x]['location'].has_key('coordinate') else None,\
					self.create_listings())
		return Longitude

	def address(self):	
		Address = map(lambda x: \
				  self.yelpresultsdict["businesses"][x]['location']['address'] if \
				  self.yelpresultsdict["businesses"][x]['location'].has_key('address') else None,\
				  self.create_listings())
		return Address

	def phone(self):
		Phone = map(lambda x: \
				self.yelpresultsdict["businesses"][x]['display_phone'] if \
				self.yelpresultsdict["businesses"][x].has_key('display_phone') else None,\
				self.create_listings())	
		return Phone

	def yelp_rating(self):
		Yelp_Rating = map(lambda x: \
					  self.yelpresultsdict["businesses"][x]['rating'] if \
					  self.yelpresultsdict["businesses"][x].has_key('rating') else None,\
					  self.create_listings())
		return Yelp_Rating

	def vote_count(self):
		Vote_Count = map(lambda x: \
			 		 self.yelpresultsdict["businesses"][x]['review_count'] if \
					 self.yelpresultsdict["businesses"][x].has_key('review_count') else None,\
					 self.create_listings())
		return Vote_Count

	def categories(self):
		Categories = map(lambda x: \
					 self.yelpresultsdict["businesses"][x]['categories'] if \
					 self.yelpresultsdict["businesses"][x].has_key('categories') else None,\
					 self.create_listings())
		return Categories

	def url(self):
		URL= map(lambda x: self.yelpresultsdict["businesses"][x]['url'] if \
						   self.yelpresultsdict["businesses"][x].has_key('url') else None,\
						   self.create_listings())
		return URL


class YelpDataExtract(YelpKeys):
	#We want only specific types of keys from the YELP API json response.
	#Later, if needed, this could be instantiated as an array.
	dataframe_colnames = ['Name','City','Latitude','Longitude','Address',\
						  'Phone','Yelp_Rating','Vote_Count','Categories','URL']

	def __init__(self, yelpresultsdict):
		super(self.__class__,self).__init__(yelpresultsdict)

	def create_yelp_dataframe(self):
		return pd.DataFrame(columns=YelpDataExtract.dataframe_colnames)	

	def populate_yelp_dataframe(self):
		yelp_df = self.create_yelp_dataframe()
		yelp_df['Name'] = self.name()
		yelp_df['City'] = self.city()
		yelp_df['Latitude'] = self.latitude()
		yelp_df['Longitude'] = self.longitude()
		yelp_df['Address'] = self.address()
		yelp_df['Phone'] = self.phone()
		yelp_df['Yelp_Rating'] = self.yelp_rating()
		yelp_df['Vote_Count'] = self.vote_count()
		yelp_df['Categories'] = self.categories()
		yelp_df['URL'] = self.url()

		return yelp_df
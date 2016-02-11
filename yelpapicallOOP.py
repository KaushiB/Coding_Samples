import rauth
import json
import argparse
import sys
import urllib
import urllib2
import numpy as np
import pandas as pd

#REFERENCES for the base code:
#http://letstalkdata.com/2014/02/how-to-use-the-yelp-api-in-python/

class YelpSearchParameters(object):
	sort = 0 #See YELP API documentation for more information.
			 #The default makes most sense, thus being hard-coded.

	def __init__(self,search_term=None,search_type=None,**kwargs):
		# Search term for the current project: 'restaurant'
		# Valid search_type: radial, city, bbox
		self.search_term = search_term
		self.search_type = search_type
		self.central_lat = kwargs.get('central_lat')
		self.central_lon = kwargs.get('central_lon')
		self.search_radius = kwargs.get('search_radius','5000') #in meters
		self.search_location = kwargs.get('search_location','San Francisco')
		self.category_filter = kwargs.get('category_filter')
		self.southwest_coords = kwargs.get('southwest_coords')
		self.northeast_coords = kwargs.get('northeast_coords')

	def radial_search(self):
		# A radial search based on a central latitude, longitude point.
		# Use a category filter to fine-tune the search, if needed. 
		params = {}
		params["term"] = self.search_term
		params["ll"] = "{},{}".format(str(self.central_lat),str(self.central_lon))
		params["radius_filter"] = self.search_radius #in meters
		params["category_filter"] = "{}".format(str(self.category_filter))
		params["sort"] = "{}".format(str(YelpSearchParameters.sort)) 

		return params

	def city_search(self):
		# Search based on a city or specific neighbourhood.
		# Use a category filter to fine-tune the search, if needed.
		params = {}
		params["term"] = self.search_term
		params["location"] = "{}".format(str(self.search_location))
		params["category_filter"] = "{}".format(str(self.category_filter))
		params["sort"] = "{}".format(str(YelpSearchParameters.sort)) 

		return params

	def boundingbox_search(self):
		# Search based on a geographical bounding box (SW-NE coordinates).
		params = {}
		sw_lat, sw_lon = list(self.southwest_coords)
		ne_lat, ne_lon = list(self.northeast_coords) 
		params["term"] = self.search_term
		params["bounds"] = "{},{}|{},{}".format(str(sw_lat),str(sw_lon),\
												str(ne_lat),str(ne_lon))

		return params

	def set_params(self):
		if (self.search_type == 'radial'):
			return self.radial_search()
		elif (self.search_type == 'city'):
			return self.city_search()
		elif (self.search_type == 'bbox'):
			return self.boundingbox_search()
		else:
			raise ValueError('Invalid search type. Please choose from radial/city/bbox.')


class YelpSessionInitiate(YelpSearchParameters):
	host = 'api.yelp.com'
	path = '/v2/search/'
	__consumer_key = 'neyH3izE9cDsWFDuW8yCtA'
	__consumer_secret = 't__k35vkc-eiXuFZ-Ik_nPBlc8s'
	__access_token = 'PK3iXgb5Wy8V8FArzZ2xo6GueJKyaK-U'
	__access_token_secret = 'YwYYexDLV4DbHsMoTi12fIuP7gk'

	def __init__(self, search_term,search_type, **kwargs):
		#Inherit the arguments from the parent class YelpSearchParameters.
		super(self.__class__,self).__init__(search_term,search_type, **kwargs)
		
	@classmethod
	def create_url(cls):
		url = 'https://{0}{1}?'.format(cls.host, urllib.quote(cls.path.encode('utf8')))
		return url

	@classmethod
	def create_session_authorization(cls):
		session = rauth.OAuth1Session(
			 	  	consumer_key = YelpSessionInitiate.__consumer_key,
				  	consumer_secret = YelpSessionInitiate.__consumer_secret,
					access_token = YelpSessionInitiate.__access_token,
					access_token_secret = YelpSessionInitiate.__access_token_secret)
		return session

	def send_session_request(self):
		request = (self.create_session_authorization()).get(url=self.create_url(),\
														params=self.set_params())
		return request

	def extract_response(self):
		#Output JSON API response as a Python dictionary.
		response = (self.send_session_request()).json()
		return response

	def extract_response_size(self):
		return (self.extract_response())['total']

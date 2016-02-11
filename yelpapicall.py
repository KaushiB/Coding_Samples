import rauth
import json
import argparse
import sys
import urllib
import urllib2
import numpy as np
import pandas as pd
from makeAgrid import makeAgrid

#REFERENCES for the base code:
#http://letstalkdata.com/2014/02/how-to-use-the-yelp-api-in-python/

file = open('Ottawa_YELP_API_grids.csv', 'w')
file.write('Bounding Box Coordinates\n')

def main():
	#Perform a geographical grid-based search on YELP API for restaurants
	#in Ottawa and the surrounding area.
	originlat = 45.2520
	originlon = -75.9800
	EWdist = 32.0
	NSdist = 24.0
	deltaEW = 2.0
	deltaNS = 2.0
	
	citygrid = makeAgrid(originlat,originlon,EWdist,NSdist,deltaEW,deltaNS)
	yelpdf = pd.DataFrame(columns=['Restaurant','City','Latitude','Longitude','Address',\
								   'Phone','Yelp_rating','Vote_Count','Categories','URL'])

	for i in range(citygrid.shape[0]-1):
		for j in range(citygrid.shape[1]-1):
			sw_coords = citygrid.iloc[i,j]
			ne_coords = citygrid.iloc[i+1,j+1]
			print 'Yelp API call for geographical bounding box: '+str(sw_coords)+'|'+str(ne_coords)
			params = get_search_parameters3(sw_coords, ne_coords)
			tempyelpdf, total_results = get_results(params)

			#Store the results of the YELP API search.
			#**IMPORTANT NOTES:**YELP API only returns 40 results for a geography-based API call.
			#Business account owners can get authorization to get more than 40, but not regular developers.
			#The JSON API response will only contain 20 out of the 40 results.
			#You must use the "offset" parameter in the API call to get the remaining 20.
			#But the sampling interval in this code is small enough to only contain 20
			#results or less (at least for Ottawa)/

			if (total_results <= 20):
				yelpdf = pd.concat([yelpdf,tempyelpdf], ignore_index=True)
				file.write('Cell'+str(i)+str(j)+','+str(sw_coords)+'|'+str(ne_coords)+','+str(total_results)+'\n')
			else:
				#Sample the grid finer by changing the sampling interval.
				if (20 < total_results <= 100):
					deltaEWsmall = 0.50
					deltaNSsmall = 0.50
				elif (total_results > 100):
					deltaEWsmall = 0.25
					deltaNSsmall = 0.25

				smallgrid = makeAgrid(list(sw_coords)[0],list(sw_coords)[1],deltaEW,deltaNS,deltaEWsmall,deltaNSsmall)
				for k in range(smallgrid.shape[0]-1):
					for l in range(smallgrid.shape[1]-1):
						sw_coords_small = smallgrid.iloc[k,l]
						ne_coords_small = smallgrid.iloc[k+1,l+1]
						print 'Yelp API call for SMALL geographical bounding box: '+str(sw_coords_small)+'|'+str(ne_coords_small)
						params_small = get_search_parameters3(sw_coords_small, ne_coords_small)
						tempyelpdf_small, total_results_small = get_results(params_small)

						yelpdf = pd.concat([yelpdf,tempyelpdf_small], ignore_index=True)
						file.write('Cell'+str(i)+str(j)+'_'+str(k)+str(l)+','+\
									str(sw_coords_small)+'|'+str(ne_coords_small)+\
									','+str(total_results_small)+'\n')

	yelpdf.to_csv('yelp_API_Ottawa.csv', encoding='utf-8', index=False)
	file.close()

	return yelpdf
	

def get_results(params):
	#INPUT:
	#	params: A string of search parameters as defined by YELP search API
	#			documentation.
	#OUTPUT:
	#	restaurandata: A Pandas dataframe containing restaurant information
	#				   extracted from the YELP search API results.
	#	response['total']: Total number of restaurants returned by the search API,
	#					   for a given radial search, city, bounding box.

	host = 'api.yelp.com'
	path = '/v2/search/'
	url = 'https://{0}{1}?'.format(host, urllib.quote(path.encode('utf8')))

	#Obtain these from Yelp's manage access page.
	#Do NOT publish these on a public forum.

	CONSUMER_KEY = 'INSERT_YOUR_OWN_KEY'
	CONSUMER_SECRET = 'INSERT_YOUR_OWN_KEY'
	TOKEN = 'INSERT_YOUR_OWN_KEY'
	TOKEN_SECRET = 'INSERT_YOUR_OWN_KEY'
  	
	session = rauth.OAuth1Session(
		consumer_key = CONSUMER_KEY
		,consumer_secret = CONSUMER_SECRET
		,access_token = TOKEN
		,access_token_secret = TOKEN_SECRET)
				
	request = session.get(url=url,params=params)
	
	#Transforms the JSON API response into a Python dictionary.
	#Extract only the required keys into a csv file.
	response = request.json()

	#print 'Total number of restaurants found in Yelp: '+str(response['total'])
	#print '-----------------------------------------------------------------------------------------------------------------------'

	colnames = ['Restaurant','City','Latitude','Longitude','Address','Phone',\
		    'Yelp_rating','Vote_Count','Categories','URL']
	restaurantdata = pd.DataFrame(columns=colnames)

	if (response['total'] < 20): 
		listing_number = np.array(xrange(response['total'])) 
	else: 
		listing_number = np.array(xrange(20))
	
	restaurantdata['Restaurant'] = map(lambda x: response["businesses"][x]['name'] if \
						     response["businesses"][x].has_key('name') else None, listing_number)
	
	restaurantdata['City'] = map(lambda x: response["businesses"][x]['location']['city'] if \
					       response["businesses"][x]['location'].has_key('city') \
					       else None, listing_number)
	
	restaurantdata['Latitude'] = map(lambda x: response["businesses"][x]['location']['coordinate']['latitude'] if \
						   response["businesses"][x]['location'].has_key('coordinate') \
						   else None, listing_number)
	
	restaurantdata['Longitude'] = map(lambda x: response["businesses"][x]['location']['coordinate']['longitude'] if \
						    response["businesses"][x]['location'].has_key('coordinate') \
						    else None, listing_number)	

	restaurantdata['Address'] = map(lambda x: response["businesses"][x]['location']['address'] if \
						  response["businesses"][x]['location'].has_key('address') \
						  else None, listing_number)

	restaurantdata['Phone'] = map(lambda x: response["businesses"][x]['display_phone'] if \
						response["businesses"][x].has_key('display_phone') \
						else None, listing_number)		

	restaurantdata['Yelp_rating'] = map(lambda x: response["businesses"][x]['rating'] if \
						      response["businesses"][x].has_key('rating') \
						      else None, listing_number)
	
	restaurantdata['Vote_Count'] = map(lambda x: response["businesses"][x]['review_count'] if \
						     response["businesses"][x].has_key('review_count') \
						     else None, listing_number)
	
	restaurantdata['Categories'] = map(lambda x: response["businesses"][x]['categories'] if \
						     response["businesses"][x].has_key('categories') \
						     else None, listing_number)

	restaurantdata['URL'] = map(lambda x: response["businesses"][x]['url'] if \
					      response["businesses"][x].has_key('url') \
					      else None, listing_number)
	
	return restaurantdata, response['total']
	
		
def get_search_parameters1(lat,lon, category_filter, sort_filter):
	#INPUT:
	# lat, lon: Central latitude and longitude for a radial search.
	# radius_filter: The search radius in meters.
	# category_filter: Category to fine-tune the search.
	#				   For example, "Sushi" for restaurants.
	# sort_filter: Default sort=0, 
	#			   see YELP search API documentation for more information.
	#OUTPUT:
	# A string with search parameters to be passed to the search API.
	
	params = {}
	params["term"] = "restaurant"
	params["ll"] = "{},{}".format(str(lat),str(lon))
	params["radius_filter"] = "20000"
	params["category_filter"] = "{}".format(str(category_filter))
	params["sort"] = "{}".format(str(sort_filter)) 

	return params

def get_search_parameters2(location,category_filter, sort_filter):
	#INPUT:
	# location: City or a specific neighbourhood for search.
	# category_filter: Category to fine-tune the search.
	#				   For example, "Sushi" for restaurants.
	# sort_filter: Default sort=0, 
	#			   see YELP search API documentation for more information.
	#OUTPUT:
	# A string with search parameters to be passed to the search API.
	
	params = {}
	params["term"] = "restaurant"
	params["location"] = "{}".format(str(location))
	params["category_filter"] = "{}".format(str(category_filter))
	params["sort"] = "{}".format(str(sort_filter)) 

	return params

def get_search_parameters3(sw_coords, ne_coords):
	#INPUT:
	# sw_coords, ne_coords: Coordinates for the SW and NE vertices of the
	#						geographical bounding box for the search API.
	#OUTPUT:
	# A string with search parameters to be passed to the search API.
	
	params = {}
	sw_lat, sw_lon = list(sw_coords) #Unpack the coordinates of the bounding box.
	ne_lat, ne_lon = list(ne_coords) 
	params["term"] = "restaurant"
	params["bounds"] = "{},{}|{},{}".format(str(sw_lat),str(sw_lon),str(ne_lat),str(ne_lon))

	return params

if __name__=="__main__":
	main()

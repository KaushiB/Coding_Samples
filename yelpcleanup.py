import pandas as pd
import numpy as np
import unicodedata
import re
global i


def yelpcleanup(yelpfile,outputfile):
	#INPUT:
	#	yelpfile: A .csv file with information from the YELP API.
	#			  The cleaning process applied here is specific to YELP search API 
	#			  output for Ottawa. ***Because its hard to fully automate data science!***
	#OUTPUT:
	#   outputfile: A .csv file with cleaned information.
	#EXAMPLE CALL:
	#	df = yelpcleanup('yelp_API_Ottawa.csv', 'yelp_API_Ottawa_new.csv')

	colnames = ['Restaurant','City','Latitude','Longitude','Address','Phone','Yelp_rating','Vote_Count','Categories','URL']
	yelpdf = pd.read_csv(yelpfile, header=0, names=colnames)

	#Filter out the two output that keeps popping up regardless of the bounding box:
	#'Wilderness Tours', 'Urbanomic Interiors'
	#Also take out some of the Aylmer, Gatineau, Hull and District de HUll restaurants,
	#They appear due to the geographical bounding box shape.

	yelpdfnew = yelpdf[~yelpdf.apply(lambda x: ((x['Restaurant'] == 'Wilderness Tours') | \
											    (x['Restaurant'] == 'Urbanomic Interiors')) | \
											    ((x['City'] == 'Aylmer') | (x['City'] == 'Gatineau') | \
											    (x['City'] == 'Hull')) | \
											    ((x['City'] == 'District de Hull')) | \
											    (x['Vote_Count'] == 0), axis=1)]

	#There are duplicates for restaurants located right on the bounding box lines.
	#You have to drop duplicates based on both name and latitude, longitude pair.
	#Otherwise, you run the risk of dropping information about chain restaurants at different locations in the city.

	#Reset indices before further manipulations. 'SettingWithCopyWarning' disappears.
	yelpdfnew = yelpdfnew.reset_index(drop=True) 
	yelpdfnew['LatLon'] = zip(yelpdfnew['Latitude'],yelpdfnew['Longitude'])
	yelpdfnew = yelpdfnew.drop_duplicates(['Restaurant','LatLon']) 
	
	#Important: Make sure to reset the indices! 
	#Otherwise, the remaining manipulations won't work, due to offset indices.
	yelpdfnew = yelpdfnew.reset_index(drop=True)

	#Convert a few of the columns into a format that is useful for Tableau Public.
	numrows = np.array(xrange(yelpdfnew.shape[0]))
	yelpdfnew['Address'] = map(lambda x: (yelpdfnew['Address'][x]).replace('[','').replace(']',''), numrows)
	
	#Clean up the category column.
	#Need to clean up the square brackets, extra commas and whitespaces, the repeat occurrences etc.

	yelpdfnew['Categories'] = yelpdfnew['Categories'].astype(str)
	yelpdfnew['Categories'] = map(lambda x: category_cleanup(yelpdfnew['Categories'][x],yelpdfnew['Categories'][x]), numrows)

	#Extract 1-3 category specifications into separate columns, for the ease of using for Tableau Public.
	yelpdfnew['Category_1'] = map(lambda x: (yelpdfnew['Categories'][x])[0] \
											 if (yelpdfnew['Categories'][x])[0] != '' \
											 else 'No Info Available', numrows)
	yelpdfnew['Category_2'] = map(lambda x: (yelpdfnew['Categories'][x])[1] \
											 if len(yelpdfnew['Categories'][x]) > 1 \
											 else 'No Info Available', numrows)
	yelpdfnew['Category_3'] = map(lambda x: (yelpdfnew['Categories'][x])[2] \
											 if len(yelpdfnew['Categories'][x]) > 2 \
											 else 'No Info Available', numrows)

	#Convert some of the really ambiguous categorical types to 'unspecified'.
	#This filtering is based on an exact match.
	category_types1 = ['restaurants','food','buffets','poolhalls','skating rinks',\
					   'arcades','piano bars','hotelstravel','hotels','venues',\
					   'venues & event spaces','casinos','comedy clubs','nan',\
					   'musicvenues','jazzandblues','nightlife']

	for i in range(len(category_types1)):
		yelpdfnew.loc[yelpdfnew['Category_1'] == category_types1[i],'Category_1'] = 'unspecified'

	#Sometimes, the same category is written in two different ways. Tokenize these types.
	#NOTE FOR IMPROVEMENT: 
	#Python has a tokenization package. Could this be better than manual tokenization?

	category_types2 = ['barbeque','breakfast','wine','tapas','sports','coffee',\
					   'canadian','american','gluten']
	category_types2_replacement = ['bbq','breakfast & brunch','wine bars',\
								   'tapas','sports bars','coffee & tea',\
								   'canadian','american','gluten free']

	for i in range(len(category_types2)):
		yelpdfnew.loc[yelpdfnew['Category_1'].str.contains(category_types2[i]), 'Category_1'] = \
					  category_types2_replacement[i]

	#Finally, take out the categorical types that has very little relevance.
	#Gas station delis or the parliment building isn't as useful as restaurants.
	yelpdfnew = yelpdfnew[~yelpdfnew['Category_1'].str.contains('carwash|gas & service stations|spas|landmarks')]
	
	yelpdfnew = yelpdfnew.reset_index(drop=True)
	numrows2 = np.array(xrange(yelpdfnew.shape[0]))
	yelpdfnew['Category_1'] = map(lambda x: (yelpdfnew['Category_1'][x]).title(), numrows2)
	
	yelpdfnew.to_csv(outputfile, index=False)

	return yelpdfnew


def category_cleanup(messy_category,clean_category):
	#INPUT:
	#	messy_category: The initial output from the YELP Python dictionary.
	#OUTPUT:
	#   clean_category: Cleaned up list.
	#					Removed extra square brackets and white spaces.
	#					Split the string elements.
	#EXAMPLE CALL:
	# 	If you want to clean up yelpdfnew['Categories'][10]...
	#	category_cleanup(yelpdfnew['Categories'][10],clean_list)

	clean_category = messy_category.replace('[','').replace(']','')
	clean_category = [i for i in re.split('[,]', clean_category) if i != '']
	clean_category = [i.lstrip().rstrip() for i in clean_category if i != '']
	clean_category = [i.lower() for i in clean_category if i != '']
	clean_category = list(set(clean_category))

	return clean_category
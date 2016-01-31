import geopy, os, sys
import pandas as pd
import numpy as np
import math
import string
from geopy.distance import VincentyDistance

def makeAgrid(lat0, lon0, distX, distY, deltaX, deltaY):

# INPUT:
#	lat0 = The origin latitude (in this case, the southernmost point)
# 	lon0 = The origin longitude (in this case, the westernmost point)
# 	distX = The west-east length of the grid.
#   distY = The south-north length of the grid.
#	deltaX = The west-east cell size in kilometers.
#	deltaY = The south-north cell size in kilometers.
#OUTPUT:
#	citygrid = A city grid with SW-NW-NE-SE coordinates of each cell, of uniform grid length (NOT angular distance).

	#Form the grid west-east and then south-north.
	origin = geopy.Point(lat0, lon0)
	bearing_north = 0
	bearing_east = 90

	#Compute the latitude and longitude of evenly-spaced (in km) points going due east, starting at the origin.
	distances_east = np.array(xrange(int(math.floor(distX/deltaX)) + 1))
	lon1 = map(lambda x: (VincentyDistance(kilometers=deltaX*x).destination(origin, bearing_east)).longitude, distances_east)
	lat1 = map(lambda x: (VincentyDistance(kilometers=deltaX*x).destination(origin, bearing_east)).latitude, distances_east) 

	#Compute the latitude and longitude of evenly-spaced (in km) points going north, for each west-east point.
	distances_north = np.array(xrange(int(math.floor(distY/deltaY)) + 1))
	colnames = map(lambda x: 'Cell'+str(x), distances_east)
	citygrid = pd.DataFrame(index=xrange(len(distances_north)), columns=colnames)

	for i in range(len(distances_east)):
		#Start from each point going eastward and calculate the coordinates of the points going northward.
		temp_origin = geopy.Point(lat1[i], lon1[i])
		temp_lon = map(lambda y: (VincentyDistance(kilometers=deltaY*y).destination(temp_origin, bearing_north)).longitude, distances_north)
		temp_lat = map(lambda y: (VincentyDistance(kilometers=deltaY*y).destination(temp_origin, bearing_north)).latitude, distances_north)
		temp_latlon = zip(temp_lat,temp_lon)
		citygrid[colnames[i]] = temp_latlon

	return citygrid






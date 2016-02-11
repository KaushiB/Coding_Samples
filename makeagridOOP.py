import geopy, os, sys
import pandas as pd
import numpy as np
import math
import string
from geopy.distance import VincentyDistance as vdist

class MakeCityGrid(object):
    bearing_north = 0
    bearing_east = 90

    def __init__(self, lat0, lon0, **kwargs):
        self.lat0 = lat0
        self.lon0 = lon0
        self.distX = kwargs.get('distX',10.)
        self.distY = kwargs.get('distY',10.)
        self.deltaX = kwargs.get('deltaX',1.)
        self.deltaY = kwargs.get('deltaY',1.)

    def set_master_origin(self):
        return geopy.Point(self.lat0, self.lon0)

    def eastward_sampling(self):
        #Distances of cell vertices starting from an origin point, going due east.
        return np.array(xrange(int(math.floor(self.distX/self.deltaX)) + 1))

    def northward_sampling(self):
        #Distances of cell vertices starting from an origin point, going due north.
        return np.array(xrange(int(math.floor(self.distY/self.deltaY)) + 1))
             
    def southwest_southeast_coords(self):
        #Starting from the master origin, compute the latitude, longitude pairs of 
        #evenly spaced (in km) cell vertices going due east.
        
        lat_due_east = \
            map(lambda x: (vdist(kilometers=self.deltaX*x).destination(self.set_master_origin(), MakeCityGrid.bearing_east)).latitude,\
                           self.eastward_sampling())
        lon_due_east = \
            map(lambda x: (vdist(kilometers=self.deltaX*x).destination(self.set_master_origin(), MakeCityGrid.bearing_east)).longitude,\
                           self.eastward_sampling())

        return zip(lat_due_east, lon_due_east)

    def set_tmp_origin(self, num):
        max_num = len(self.southwest_southeast_coords())
        if (num > max_num):
            raise ValueError('Argument must be less than '+str(max_num))
        else:
            return geopy.Point(self.southwest_southeast_coords()[num])

    def northwest_northeast_coords(self, num):
        #Starting from an origin point, compute the latitude, longitude pairs of
        #evenly spaced (in km) cell vertices going due north.
        #The origin point is extracted from "set_tmp_origin" besed on the points
        #along the west-east line.

        lat_due_north = \
            map(lambda x: (vdist(kilometers=self.deltaY*x).destination(self.set_tmp_origin(num),MakeCityGrid.bearing_north)).latitude,\
                           self.northward_sampling())
        lon_due_north = \
            map(lambda x: (vdist(kilometers=self.deltaY*x).destination(self.set_tmp_origin(num),MakeCityGrid.bearing_north)).longitude,\
                           self.northward_sampling())

        return zip(lat_due_north, lon_due_north)

    def populate_citygrid(self):
        #Create a dataframe to save the latitude, longitude pairs of the city grid.
        colnames = map(lambda x: 'Cell'+str(x).zfill(3), self.eastward_sampling())
        citygrid = pd.DataFrame(index=xrange(len(self.northward_sampling())),\
                                columns=colnames)
        
        #For each vertex along the west-east line, compute the latitude, longitude 
        #pairs of evenly spaced (in km) cell vertices going due north.
        for i in range(len(colnames)):
            citygrid[colnames[i]] = self.northwest_northeast_coords(i)

        return citygrid
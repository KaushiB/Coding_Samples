import sys, os
import numpy as np
import pandas as pd
from makeagrid import MakeCityGrid
from yelpapicall import YelpSearchParameters
from yelpapicall import YelpSessionInitiate
from yelpapikeys import YelpKeys 
from yelpapikeys import YelpDataExtract
import logging

def main():
    #Perform a geographical grid-based search on YELP API for restaurants
    #in Ottawa and the surrounding area.
    
    #**IMPORTANT NOTES:**YELP search API only returns 40 results for a geography-based API call. 
    #Business account owners can get authorization to get more than 40, 
    #but not regular developers. 
    #The API response will only output 20 out of the 40 results.
    #You must use the "offset" parameter in the API call to get the remaining 20.
    #But the geographical cells in this code is small enough to only contain 20
    #results or less (at least for Ottawa).

    #Listing of the processes for the geographical grid-based search.
    #   proc1 = MakeCityGrid
    #   proc2 = YelpSessionInitiate
    #   proc3 = YelpDataExtract

    #Set the log file.
    log_filename = 'yelpsearch.log'
    logging.basicConfig(filename=log_filename,level=logging.INFO)

    #Set up the search geographical search parameters.
    originlat = 45.2520
    originlon = -75.9800
    EWdist = 32.0
    NSdist = 24.0
    deltaEW = 2.0
    deltaNS = 2.0

    kwargs1 = {'distX':EWdist, 'distY':NSdist, 'deltaX':deltaEW, 'deltaY':deltaNS}
    proc1 = MakeCityGrid(originlat,originlon,**kwargs1)
    ottawagrid = proc1.populate_citygrid()

    #Main dataframe to store the results.
    colnames = ['Name','City','Latitude','Longitude','Address','Phone',\
                'Yelp_rating','Vote_Count','Categories','URL']
    yelpdf = pd.DataFrame(columns=colnames)

    for i in range(ottawagrid.shape[0]-1):
        for j in range(ottawagrid.shape[1]-1):
            sw_coords = ottawagrid.iloc[i,j]
            ne_coords = ottawagrid.iloc[i+1,j+1]
            logging.info('Yelp API call for geographical bounding box: '+\
                                              str(sw_coords)+'|'+str(ne_coords))

            kwargs2 = {'southwest_coords':sw_coords,'northeast_coords':ne_coords}
            proc2 = YelpSessionInitiate(search_term='restaurant',search_type='bbox',**kwargs2)
            logging.info('Total results within the cell: '+str(proc2.extract_response_size()))
            logging.info('--------------------------------------------------------------------------------')
            
            if (proc2.extract_response_size() <= 20):
                proc3 = YelpDataExtract(proc2.extract_response())
                yelpdf = pd.concat([yelpdf,proc3.populate_yelp_dataframe()],\
                                    ignore_index=True)
            else:
                #Use a finer sampling within a denser cell to extract all results.
                if (20 < proc2.extract_response_size() <= 100):
                    deltaEWsmall = 0.50
                    deltaNSsmall = 0.50
                elif (proc2.extract_response_size() > 100):
                    deltaEWsmall = 0.25
                    deltaNSsmall = 0.25

                small_lat = list(sw_coords)[0]
                small_lon = list(sw_coords)[1]
                kwargs1v2 = {'distX':deltaEW, 'distY':deltaNS, \
                             'deltaX':deltaEWsmall, 'deltaY':deltaNSsmall}
                proc1v2 = MakeCityGrid(small_lat,small_lon,**kwargs1v2)
                smallgrid = proc1v2.populate_citygrid()

                for k in range(smallgrid.shape[0]-1):
                    for l in range(smallgrid.shape[1]-1):
                        sw_coords_small = smallgrid.iloc[k,l]
                        ne_coords_small = smallgrid.iloc[k+1,l+1]
                        logging.info('Yelp API call for SMALL geographical bounding box: '+\
                                   str(sw_coords_small)+'|'+str(ne_coords_small))

                        kwargs2v2 = {'southwest_coords':sw_coords_small,\
                                     'northeast_coords':ne_coords_small}
                        proc2v2 = YelpSessionInitiate(search_term='restaurant',\
                                                 search_type='bbox',**kwargs2v2)
                        
                        logging.info('Total results within the SMALL cell: '+\
                                              str(proc2v2.extract_response_size()))
                        logging.info('--------------------------------------------------------------------------------')
                        
                        proc3v2 = YelpDataExtract(proc2v2.extract_response())
                        yelpdf = pd.concat([yelpdf,proc3v2.populate_yelp_dataframe()],\
                                                              ignore_index=True)


    yelpdf.to_csv('yelp_API_Ottawa.csv',encoding='utf-8',columns=colnames,index=False)

if __name__=="__main__":
    main()
from app import app, app_config, hubspotDeals
from flask_socketio import SocketIO, emit, disconnect  
import time
import threading
import logging
import random
import requests
import json
import os 

#
# check for new closed deals
#
def getDealId():
    response = requests.get("https://aqueous-wave-55186.herokuapp.com/getDeal")
    response = requests.get( app_config.appConfig['HEROKU']['newDealEndPoint'] )
    if response.status_code == 200:
        test = response.json()
        dealID = test['dealID']
    else:
        dealID = 0
    return dealID

#
# return a random music file
#

def getRndMusicFln():
    random.seed()
    musicDir        = getMusicFilesInDir()
    musicFilesNo    = len( musicDir)
    musicRndIdx     = random.randrange(1,musicFilesNo+1)
    musicRndFln     = list(  musicDir )[musicRndIdx-1]
    logging.info ("rnd file   =" + musicRndFln)
    return musicRndFln

#
# get list of music files
#
def getMusicFilesInDir():

    staticDir = app_config.appConfig['THREAD']['musicDir']

    uploadDir = {}

    with os.scandir(staticDir) as entries:
        for entry in entries:
            if entry.is_file():
                uploadDir[entry.name] = entry.path

    return uploadDir



def background_thread():
    while True:
        time.sleep(int(app_config.appConfig['THREAD']['sleep_seconds']))
        logging.info ("Checking for new deals")
        dealID = getDealId()

        if dealID > 0 :#and prevDealID != dealID:
            logging.info ("Found deal - " + str(dealID)) 
            dealInfo    = hubspotDeals.getDealDetails(dealID)
            dealOwner   = hubspotDeals.getDealOwner(dealInfo ['properties']['hubspot_owner_id']['value'])
            firstName   = dealOwner['firstName']
            lastName    = dealOwner['lastName']
            # get a random music file
            musicFln    =  getRndMusicFln()

            app_config.socketio.emit('new_deal', {'data': 'Deal Closed ', 'ID': dealID, 'Name' : dealInfo ['properties']['dealname']['value']  , 'Value' :  dealInfo ['properties']['amount']['value'] , 'firstName' : firstName, 'lastName' : lastName, 'musicFln' : musicFln },
                          namespace='/index')
            prevDealID = dealID

            #
            # update deal tables
            #
            hubspotDeals.getRecentDeals()
            sortedDollarTable = hubspotDeals.getDealTotalDollar()
            sortedCountTable  = hubspotDeals.getDealTotalCount()

            app_config.socketio.emit('totalDollar', sortedDollarTable, namespace='/index')
            app_config.socketio.emit('totalCount', sortedCountTable, namespace='/index')



#
# starting thread
#
background_thread = threading.Thread(target=background_thread, args=(),daemon=True)
background_thread.start()

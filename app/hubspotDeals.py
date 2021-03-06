
import requests
import datetime
import time
import requests
import datetime
import time
import logging
from app import app, app_config


#setup empty deal tables

dealTotalDollar         = {}
dealTotalCount          = {}
sortedDealTotalDollar   = {}
sortedDealTotalCount    = {}
ownerDetails            = {}
dealSumaryRunning       = False



def getLastMondayTS():
    #today           = datetime.date.today()
    #lastMonday      = today - datetime.timedelta(days=today.weekday())
    #lastMondayTS    = int(time.mktime(lastMonday.timetuple() ) )
    today           = datetime.date.today()
    lastMonday      = today 
    lastMondayTS    = int(time.mktime(lastMonday.timetuple() ) )
    return  str(lastMondayTS * 1000 )

#
# Get owner details from HubSpot and cache results
#     
def getDealOwner(ownerId):
    global ownerDetails

    if (ownerId in ownerDetails.keys() ):
        logging.info("owner in cache " + str(ownerId))
        return ownerDetails[ownerId]
    else:
        logging.info("owner NOT in cache " + str(ownerId))
        response = requests.get(  app_config.appConfig['HUBSPOT']['getOwnerEndPoint'] + str(ownerId) + "?hapikey=" + app_config.appConfig['HUBSPOT']['apiKey'])
        resJson = response.json()

        ownerDetails[ownerId]={}
        if ( (resJson['firstName'] == "") and (resJson['lastName'] == "")):
            ownerDetails[ownerId]['firstName']  = resJson['email'].partition(".")[0].capitalize() 
            ownerDetails[ownerId]['lastName']   = resJson['email'].replace("@yellow.co.nz","").partition(".")[2].capitalize() 
        else:
            ownerDetails[ownerId]['firstName']=resJson['firstName'].capitalize()
            ownerDetails[ownerId]['lastName']=resJson['lastName'].capitalize()
        return ownerDetails[ownerId]

def getDealDetails(dealId):
    response = requests.get( app_config.appConfig['HUBSPOT']['getDealEndPoint'] + str(dealId) + "?hapikey=" + app_config.appConfig['HUBSPOT']['apiKey'])
    resJson = response.json()
    return response.json()

def addDealToTables(deal):
    global dealTotalDollar
    global dealTotalCount 
    owner                                       = deal['properties']['hubspot_owner_id']['value']
    ownerDetail = getDealOwner(owner)


    if owner in dealTotalDollar:
        dealTotalDollar[owner]['totalDollar']   =  float ( dealTotalDollar[owner]['totalDollar'])  + float(deal['properties']['hs_closed_amount']['value'])
    else:
        dealTotalDollar[owner]                  =  {}
        dealTotalDollar[owner]['firstName']     =  ownerDetail["firstName"]
        dealTotalDollar[owner]['lastName']      =  ownerDetail["lastName"]
        dealTotalDollar[owner]['totalDollar']   =  float(deal['properties']['hs_closed_amount']['value'])

    if owner in dealTotalCount:
        dealTotalCount[owner]['totalDeals']     =  int( dealTotalCount[owner]['totalDeals'])  + 1
    else:
        dealTotalCount[owner]                   =  {}
        dealTotalCount[owner]['firstName']      =  ownerDetail["firstName"]
        dealTotalCount[owner]['lastName']       =  ownerDetail["lastName"]
        dealTotalCount[owner]['totalDeals']     =  1
    
    

def sortDealTable(dictToSort, sortKey):

    sortedTable = {}
    sortedKeys  =  sorted(dictToSort, key=lambda x: (dictToSort[x][sortKey]) ,reverse=True ) 
    rank        = 0

    for key in sortedKeys:
        rank +=1
        sortedTable[rank] = dictToSort[key]

    sortedTable['NoOfRows']   = rank
    return sortedTable


def getDealTotalDollar():
    global sortedDealTotalDollar
    return sortedDealTotalDollar

def getDealTotalCount():
    global sortedDealTotalCount
    return sortedDealTotalCount

def getRecentDeals():

    #
    # clear deal tables
    #
    global dealTotalDollar
    global dealTotalCount
    global sortedDealTotalDollar
    global sortedDealTotalCount
    global dealSumaryRunning
    
    if dealSumaryRunning: 
        return
    
    dealSumaryRunning = True

    dealTotalDollar         = {}
    dealTotalCount          = {}
    # 
    # get last Sun/Mon midnight
    #
    lastMondayTS    = getLastMondayTS()

    apiOffset       = 0
    dealGetURLBase  = app_config.appConfig['HUBSPOT']['getRecentDealsEndPoint'] + "?hapikey=" +  app_config.appConfig['HUBSPOT']['apiKey'] + '&since=' + lastMondayTS + '&count=' +  app_config.appConfig['HUBSPOT']['dealRetreiveCount']
    dealGetURL      = dealGetURLBase + '&offset='+ str(apiOffset) 

    logging.info ("Deal URL : " + dealGetURL)
    response        = requests.get( dealGetURL )
    resJson         = response.json()
    moreData        = True


    while moreData:
        for deal in resJson['results']:
            #
            # check if deal is offline and closed
            #
            if (deal['isDeleted']                                == False and
                deal['properties']['pipeline']['value']          ==  app_config.appConfig['HUBSPOT']['offlineDealPipeline'] and
                str(deal['properties']['dealstage']['value'])    ==  app_config.appConfig['HUBSPOT']['OfflineClosedWon']):
                    #
                    # check if the deal was closed won this week
                    #
                    if 'closedate' in deal['properties'].keys():
                        if int(deal['properties']['closedate']['value']) > int(lastMondayTS) :
                            addDealToTables(deal)

             
        if  resJson['hasMore'] == True:
            #
            # get next block of modified deals
            #
            apiOffset   = resJson['offset']
            dealGetURL  = dealGetURLBase + '&offset='+ str(apiOffset) 
            response    = requests.get( dealGetURL )
            logging.info (dealGetURL)
            resJson     = response.json()
        else:
            moreData    = False
    #
    # Sort tables
    #
    sortedDealTotalDollar = sortDealTable(dealTotalDollar,'totalDollar') 
    sortedDealTotalCount  = sortDealTable(dealTotalCount,'totalDeals') 
    dealSumaryRunning = False



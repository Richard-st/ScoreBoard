from app import app, app_config, hubspotDeals
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, disconnect  

#
# Globals
#

broadcastTables      = {}
sortedDollarTable    = {}
sortedCountTable     = {}

#
# main display
#
@app.route('/')
def index():
    return render_template('index.html', async_mode=app_config.socketio.async_mode)


#
# when a client browser connects to /index, send tables to browser
#
@app_config.socketio.on('connect'  , namespace='/index')
def initalBrowserConnect():
    global broadcastTables
    global sortedDollarTable
    global sortedCountTable

    #
    # if we dont have the deal table information, refresh. Shol donly be required on server startup
    #
    if not sortedDollarTable:
        print ('Refreshing Deals' )
        hubspotDeals.getRecentDeals()
        sortedDollarTable = hubspotDeals.getDealTotalDollar()
        sortedCountTable  = hubspotDeals.getDealTotalCount()

    #
    # send tables to browsers
    #
    app_config.socketio.emit('totalDollar', sortedDollarTable, namespace='/index')
    app_config.socketio.emit('totalCount', sortedCountTable, namespace='/index')    

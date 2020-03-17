from app import app
import configparser
from flask_socketio import SocketIO, emit, disconnect  


appConfig = configparser.ConfigParser()
appConfig.read('app/app.ini')

#
# Globals
#
async_mode                  = None
socketio                    = SocketIO(app, async_mode=async_mode)

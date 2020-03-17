from flask import Flask
import logging


app = Flask(__name__)

from app import app_config
from app import logger
from app import views
from app import admin_views
from app import thread
from app import app, app_config
import time
import threading
import logging


def background_thread():
    logging.info("Thread started ")
    while True:
        logging.info("Thread running ")
        time.sleep(int(app_config.appConfig['THREAD']['sleep_seconds']))


#
# starting thread
#
background_thread = threading.Thread(target=background_thread, args=(),daemon=True)
background_thread.start()

import sys
import os
from shutil import copy
from shutil import rmtree
import sqlite3
import win32api, win32con, win32gui
import threading
from time import sleep
from app import *


os.system('cls')

print("SODA: Small Sensor Organizing Database Application")
# Adding a few little sleep delays to give the user
# a moment to verify the config settings are correct
#sleep(2)

try:
    import config
except:
    print("No config.py file found. Quitting...")
    sys.exit()

storage_path = config.STORAGE_PATH
project_name = config.PROJECT_NAME.upper()
project_path = os.path.join(storage_path, project_name)
database_name = project_name + ".db"
database_path = os.path.join(project_path,database_name)
project_exists = os.path.exists(project_path)

# SessionInfo objects, just a handy way to pass session data to functions
class SessionInfo(object):
    def __init__(self, project_name, project_path, storage_path, \
            db_name, db_path, exists, location_name=None, location_id=None):
        SessionInfo.name = project_name
        SessionInfo.path = project_path
        SessionInfo.storage_path = storage_path
        SessionInfo.db_name = db_name
        SessionInfo.db_path = db_path
        SessionInfo.location_name = location_name
        SessionInfo.location_id = location_id
        SessionInfo.exists = exists

# Declare a new object without location ID, we'll get that in a minute
session = SessionInfo(project_name, project_path, storage_path, database_name, database_path, project_exists)

global DRIVE
DRIVE = None

displayConfigInfo(session)
existingProjectDialogue(session)
conn = connectToDB(session)
c = conn.cursor()

# location name dialogue and id retrieval

locations = getLocations(c)
session.location_name = selectLocationName(locations)
session.location_id = getLocationID(c, session.location_name)

print("YOU HAVE SELECTED LOCATION " + session.location_name + " with id " + str(session.location_id))

closeDB(conn)

# Start windows message loop in its own thread because it's blocking
if __name__ == '__main__':

    # Flags to communicate that a device has arrived or departed, and to stop the
    # message loop (PumpMessages) when it's time to quit.
    deviceFlag = threading.Event()
    stopThreadFlag = threading.Event()

    def winLoop(stopthreadFlag, deviceFlag):
        global DRIVE
        w = Notification(stopThreadFlag, deviceFlag)
        win32gui.PumpMessages()
    
    SDlisten = threading.Thread(name='message loop', target=winLoop, args=(stopThreadFlag, deviceFlag))
    SDlisten.start()
        
#
# Main program loop
#
command = 'none'
files = cardRead(command, deviceFlag, session)
try:
    while (True):
        if command[0] != 'a':
            command = commandPrompt(files, stopThreadFlag)
        if command[0] == 'q':
            break
        cardRead(command, deviceFlag, session)
except Exception as e:
    print(e)
    command = 'q'

print("this is the end...")
if command[0] == 'q':
    SDlisten.join()
    closeDB(conn)
    print('Bye!')


    # sample data tuples
    # sameplesensor = (1, 1, 1, 1, 1, 1, 1, 1, 1, '2017
    # sensorinsert = '''INSERT INTO sensors 1, 1, 1, 1, 1, 1, 1, 1, 1, date('now')'''

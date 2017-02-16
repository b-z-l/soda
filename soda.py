import sys
import os
from shutil import copy
from shutil import rmtree
import sqlite3
import win32api, win32con, win32gui
from ctypes import *
import threading
from time import sleep
from app import *


### Main program entry here

os.system('cls')

print("SODA: Sensor Organizing Data Application")
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
global DRIVE
DRIVE = None


displayConfigInfo(storage_path, project_name)


existingProjectDialogue(project_name, project_path, database_path)

conn = connectToDB(database_path, projectExists)
# a cursor object is used to execute database inserts and queries
c = conn.cursor()

# location dialogue

locations = getLocations(c)
#if (locations == None):
 #   command = "no"
  #  while (command != "yes"):
   #     location_name = input("Please enter the name of new sensor location: ")
    #    print()
     #   command = input("Location name: " + location_name + "\n\n Does this look okay (yes or no)?")
#else:
command = "no"
while (command != "yes"):
    print("Please select location of sensor(s): ")
    print("This is important data to later select sensor data based on where it was.")
    print()

    for i in range(len(locations)):
        print("     " + str(i+1) + ": " + str(locations[i][1]))
    newOption = len(locations) + 1
    print("     " + str(newOption) + ": " + "Add a new location")
    print()
    loc_select = -1
    # while (loc_select < int(locations[0][0]) or loc_select > newOption): 
    while (loc_select < 1 or loc_select > newOption): 
        try:
            loc_select = int(input("Please enter a number to select an option: "),10)
        except:
            loc_select = -1
    if (loc_select == newOption):
        location_name = input("Please enter the name of new sensor location: ")
    else:
        location_name = locations[loc_select-1][1]
    command = input("Location name: " + location_name + "\nDoes this look okay (yes or no)? ")

location_id = getLocationID(c, location_name)
print("YOU HAVE SELECTED LOCATION " + location_name + " with id " + str(location_id))
closeDB(conn)


if __name__ == '__main__':
    
    yesDeviceFlag = threading.Event()
    stopThreadFlag = threading.Event()

    def winLoop(stopthreadFlag, yesDeviceFlag):
        global DRIVE
        global w
        w = Notification(stopThreadFlag, yesDeviceFlag)
        win32gui.PumpMessages()
        #while(1):
        #    win32gui.PumpWaitingMessages()
        #    sleep(.1)
    
    SDlisten = threading.Thread(name='message loop', target=winLoop, args=(stopThreadFlag, yesDeviceFlag))
    SDlisten.start()
        

### Main program loop



command = 'none'
files = cardRead(command, yesDeviceFlag)
try:
    while (True):
        if command[0] != 'a':
            command = commandPrompt(files)
        if command[0] == 'q':
            break
        cardRead(command, yesDeviceFlag)
except Exception as e:
    print(e)
    command = 'q'

global w
print("this is the end...")
if command[0] == 'q':
   #win32gui.sendmessage
   # w.onDestroy()
    SDlisten.join()
    closeDB()
    print('Bye!')


    # sample data tuples
    # sameplesensor = (1, 1, 1, 1, 1, 1, 1, 1, 1, '2017
    # sensorinsert = '''INSERT INTO sensors 1, 1, 1, 1, 1, 1, 1, 1, 1, date('now')'''

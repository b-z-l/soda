import sys
import os
from shutil import copy
import sqlite3
import win32api, win32con, win32gui
from ctypes import *
import threading
from time import sleep


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        super(StoppableThread, self).__init__()
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

#
# Device change events (WM_DEVICECHANGE wParam)
#
DBT_DEVICEARRIVAL = 0x8000
DBT_DEVICEQUERYREMOVE = 0x8001
DBT_DEVICEQUERYREMOVEFAILED = 0x8002
DBT_DEVICEMOVEPENDING = 0x8003
DBT_DEVICEREMOVECOMPLETE = 0x8004
DBT_DEVICETYPESSPECIFIC = 0x8005
DBT_CONFIGCHANGED = 0x0018

#
# type of device in DEV_BROADCAST_HDR
#
DBT_DEVTYP_OEM = 0x00000000
DBT_DEVTYP_DEVNODE = 0x00000001
DBT_DEVTYP_VOLUME = 0x00000002
DBT_DEVTYPE_PORT = 0x00000003
DBT_DEVTYPE_NET = 0x00000004

#
# media types in DBT_DEVTYP_VOLUME
#
DBTF_MEDIA = 0x0001
DBTF_NET = 0x0002

WORD = c_ushort
DWORD = c_ulong
class DEV_BROADCAST_HDR(Structure):
    _fields_ = [
        ("dbch_size", DWORD),
        ("dbch_devicetype", DWORD),
        ("dbch_reserved", DWORD)
    ]


class DEV_BROADCAST_VOLUME(Structure):
    _fields_ = [
        ("dbcv_size", DWORD),
        ("dbcv_devicetype", DWORD),
        ("dbcv_reserved", DWORD),
        ("dbcv_unitmask", DWORD),
        ("dbcv_flags", WORD)
    ]


def drive_from_mask(mask):
    n_drive = 0
    while 1:
        if (mask & (2 ** n_drive)):
            return n_drive
        else:
            n_drive += 1


class Notification():
    def __init__(self):
        message_map = {
            win32con.WM_DEVICECHANGE: self.onDeviceChange,
	    win32con.WM_DESTROY: self.onDestroy
        }

        wc = win32gui.WNDCLASS()
        hinst = wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = "DeviceChangeDemo"
        wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
        wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        wc.hbrBackground = win32con.COLOR_WINDOW
        wc.lpfnWndProc = message_map
        classAtom = win32gui.RegisterClass(wc)
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow(
            classAtom,
            "Device Change Demo",
            style,
            0, 0,
            win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
            0, 0,
            hinst, None
        )
    def onDestroy(hwnd, msg, wparam, lparam):
        win32gui.PostQuitMessage(0)
        print("I DIE")
        return

    def onDeviceChange(self, hwnd, msg, wparam, lparam):
        #
        # WM_DEVICECHANGE:
        #  wParam - type of change: arrival, removal etc.
        #  lParam - what's changed?
        #    if it's a volume then...
        #  lParam - what's changed more exactly
        #
        global DRIVE
        dev_broadcast_hdr = DEV_BROADCAST_HDR.from_address(lparam)

        if wparam == DBT_DEVICEARRIVAL:
            #print("Something's arrived")

            if dev_broadcast_hdr.dbch_devicetype == DBT_DEVTYP_VOLUME:
                #print("It's a volume!")

                dev_broadcast_volume = DEV_BROADCAST_VOLUME.from_address(lparam)
                if dev_broadcast_volume.dbcv_flags & DBTF_MEDIA:
                    print("with some media")
                drive_letter = drive_from_mask(dev_broadcast_volume.dbcv_unitmask)
                DRIVE = chr(ord("A") + drive_letter) + ':\\'                       
                print("Drive", DRIVE, "inserted")
                yesDevice.set()
        if wparam == DBT_DEVICEREMOVECOMPLETE:
                DRIVE = None
                print("Safe to remove drive")
                #print ("Drive ", chr(ord("A") + drive_letter, " being ejected!"));

        return 1


# function for creating new project directory
def newProject():
    print("Creating new directory " + project_path + ".......", end="")
    # make project file path
    try:
        os.makedirs(project_path)
    except Exception as e:
        print()
        print("Error: Couldn't create new directory")
        print(e)
        sys.exit()
    print("OKAY")

# connect to database code is the same whether accessing existing or creating new
# returns a sqlite3 connection object used to interact with the database
def connectToDB(path_to_db_file, project_exists):
    print("Connecting to database at " + database_path + ".......", end="")
    try:
        conn = sqlite3.connect(path_to_db_file)
    except Exception as e:
        print()
        print("Error: Couldn't connect to the database")
        print(e)
        sys.exit()
    print("OKAY")
    
    if (not project_exists):
        try:
            import schema
        except Exception as e:
            print()
            print("Error: Couldn't find schema.py. This should be a file with a list named schema holding tuples which contain one sqlite CREATE command each")
            print(e)
            sys.exit()

        try:
            c = conn.cursor()
            print("Creating new database schema.......",end="")
            for i in schema.schema:
                c.execute(i[0])
        except Exception as e:
            print("Error: Problem creating new database")
            print(e)
        print("OKAY")
                
    return conn

def closeDB(conn):
    conn.commit()
    conn.close()
    print("Database closed.")

# getLocations
# argument: 
#   c: sqlite3 cursor object
# returns:
#  list of (id, location_name) tuples or
#  None if none found
def getLocations(c):
    locations_c = c.execute('''SELECT * FROM locations''')
    location = locations_c.fetchone()
    locations = [];
    while (location != None):
        locations.append(location)
        location = locations_c.fetchone()
    return locations
            
# getLocationID
# arguments:
#   cursor object, c
#   string, location name to get id for
# returns:
#   integer - location id
def getLocationID(c, location):
    loc_t = (location,)
    result = c.execute('''SELECT id FROM locations WHERE location = ?''', loc_t)
    id = result.fetchone()
    if (id != None):
        return id[0]
    else:
        c.execute('''INSERT INTO locations VALUES (NULL, ?)''', loc_t)
        result = c.execute('''SELECT last_insert_rowid()''')
        id = result.fetchone()
        return id[0]
    

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

# Config display

print("Configuration settings imported from config.py")
print("Configuration check:")
#sleep(2)
print()
print("     STORAGE_PATH: " + storage_path)
print("     PROJECT_NAME: " + project_name)
print()
#sleep(3)

# Project existence dialog

projectExists = os.path.exists(project_path)

if (projectExists):
    print("*** The " + project_name + " project directory already exists at: \n\t" + project_path)
    print()
    print("*** If you continue you will be importing data into that\n    project folder and database.")
else:
    print("Project " + project_name + " does not currently exist at specified STORAGE_PATH");
    print()
    print("     A new project folder will be created at " + project_path)
    print("     A new database file will be created at " + database_path)


print()
command = ""
while (command != "yes" and command != "no"):
    command = input("Are you sure you want to continue (yes or no)? ")

if (command == "no"):
    print("Okay! Quitting...")
    sys.exit()

if (not projectExists):
    newProject()

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
    
    yesDevice = threading.Event()
    stopThread = threading.Event()

    def winLoop():
        global DRIVE
        w = Notification()
        while(1):
            win32gui.PumpWaitingMessages()
            sleep(.1)
        print("wth man")
    
    worker1 = threading.Thread(name='message loop', target=winLoop)
    worker1.start()
        

### Main program loop

months = {
    '0':'Unknown',
    '1':'January',
    '2':'February',
    '3':'March',
    '4':'April',
    '5':'May',
    '6':'June',
    '7':'July',
    '8':'August',
    '9':'September',
    '10':'October',
    '11':'November',
    '12':'December'
}

while (True): 
    if (DRIVE != None):
        command = input("What do you want to do? ")
        if (command == 'get'):
            files = os.listdir(path=DRIVE)
            print(files)
        elif (command == 'e'):
            removedrive = 'removedrive ' + DRIVE + ' -L'
            o = os.popen(removedrive).read()
        elif (command == 'q'):
            win32gui.PostQuitMessage(0)
            removedrive = 'removedrive ' + DRIVE + ' -L'
            o = os.popen(removedrive).read()
            break
    else:
        print("(Re)Insert an SD card with sensor datas!")
        # wait for a drive to show up
        yesDevice.wait()
        yesDevice.clear()
        files = os.listdir(path=DRIVE) #get paths too
        files = [i for i in files if 'SENSOR' in i]
        if (len(files) == 0):
            print("No sensor files found on this drive :(")
        else:
            try:
                file_info = []
                for f in files:
                    # construct potential destination path
                    # project_path\location\Jan\1\SENSOR001\
                    f_s = f.split('_')
                    month = months[f_s[1]] if int(f_s[1]) in range(1,12) else months['0']
                    dest_path = os.path.join(project_path, location_name, f_s[0], month)
                    # build this tuple (filename,currpath,destpath,toTransfer)
                    file_info.append(
                        (f, 
                        os.path.join(DRIVE,f), 
                        dest_path, 
                        not os.path.exists(os.path.join(dest_path,f)))
                    )
                print(file_info)
              #  fileData = getFileData
                # data we need: current file path, file destination path
                # does the file already exist, in dest dir?
            except Exception as e:
                    print(e)

            


    print("this is the end...")


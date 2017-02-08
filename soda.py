import sys
from os import makedirs
from os import path
from os import system
from shutil import copy
import sqlite3
from time import sleep


# function for creating new project directory
def newProject():
    print("Creating new directory " + project_path + ".......", end="")
    # make project file path
    try:
        makedirs(project_path)
    except Exception as e:
        print()
        print("Error: Couldn't create new directory")
        print(e)
        sys.exit()
    print("OKAY")

# connect to database code is the same whether accessing existing or creating new
# returns a sqlite3 connection object used to interact with the database
def connectToDB(path_to_db_file):
    print("Connecting to database at " + database_path + ".......", end="")
    try:
        conn = sqlite3.connect(path_to_db_file)
    except Exception as e:
        print()
        print("Error: Couldn't connect to the database")
        print(e)
        sys.exit()
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
#  list of locations or
#  None if none found
def getLocations(c):
    locations_c = c.execute('''SELECT * FROM locations''')
    location = locations_c.fetchone()
    if (location == None):
        return None
    else:
        locations = [];
        while (location != None):
            locations.append(location[1])
            location = location_c.fetchone()
    return locations
            
# getLocationID
# arguments:
#   sqlite3 cursor object, c
#   string, location name to get id for
# returns:
#   integer - location id
def getLocationID(c, location):
    result = c.execute('''SELECT id FROM locations WHERE location = ?''', location)
    id = result.fetchone()
    if (id != None):
        return id[0]
    else:
        c.execute('''INSERT INTO locations VALUES (NULL, ?)''', location)
        result = c.execute('''SELECT last_insert_rowid()''')
        id = result.fetchone()
        return id[0]
    

# Main program entry here

system('cls')

print("SODA: Sensor Organizing Data Application")
# Adding a few little sleep delays to give the user
# a moment to verify the config settings are correct
sleep(2)
try:
    import config
except:
    print("No config.py file found. Quitting...")
    sys.exit()

storage_path = config.STORAGE_PATH
project_name = config.PROJECT_NAME.upper()
project_path = path.join(storage_path, project_name)
database_name = project_name + ".db"
database_path = path.join(project_path,database_name)

# Config display

print("Configuration settings imported from config.py")
print("Configuration check:")
sleep(2)
print()
print("     STORAGE_PATH: " + storage_path)
print("     PROJECT_NAME: " + project_name)
print()
sleep(3)

# Project existence dialog

projectExists = path.exists(project_path)

if (projectExists):
    print("*** The " + project_name + " project directory already exists at " + project_path)
    print("*** If you continue you will be importing data into that project folder and database.")
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

conn = connectToDB(database_path)
# a cursor object is used to execute database inserts and queries
c = conn.cursor()

locations = getLocations(c)
setLocation(c)

### DATABASE TESTING
c.execute("""CREATE TABLE IF NOT EXISTS awesomepossum(row_id INTEGER PRIMARY KEY, name text NO NULL)""")
c.execute("""INSERT INTO awesomepossum VALUES(NULL, "Billy")""")
print("INSERT BABY")
closeDB(conn);


























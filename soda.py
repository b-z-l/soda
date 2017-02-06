import sys
from os import makedirs
from os import path
from os import system
from shutil import copy
from time import sleep
import sqlite3


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
    print("OK")

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
    print("OK")
    return conn

def closeDB(conn):
    conn.commit()
    conn.close()
    print("Database closed.")

# Main program entry here
system('cls')

print("SODA: Sensor Organizing Data Application")
print()
# i'm adding sleep delays, superfluous? maybe
# it's good for human info processing in my humble opinion 

#sleep(.5)
try:
    import config
except:
    print("No config file found. Quitting...")
    sys.exit()

storage_path = config.STORAGE_PATH
project_name = config.PROJECT_NAME.upper()
project_path = path.join(storage_path, project_name)
database_name = project_name + ".db"
database_path = path.join(project_path,database_name)


print("Configuration settings imported from config.py")
#sleep(1)
print("Configuration check:")
print()
print("     Data storage path: " + storage_path)
print("     Project name: " + project_name)
print()

projectExists = path.exists(project_path)

if (projectExists):
    print("The " + project_name + " project directory already exists at " + project_path)
    print("***If you continue you will be importing data into that project folder and database.***")
else:
    print("Project " + project_name + " does not currently exist")
    print("A new project folder will be created at " + project_path)
    print("A new database file will be created at " + database_path)


print()
command = ""
while (command != "yes" and command != "no"):
    command = input("Are you sure you want to continue (yes or no)? ")

if (command == "no"):
    print("OK! Quitting...")
    sys.exit()

if (not projectExists):
    newProject()

conn = connectToDB(database_path)
# a cursor object is used to execute database inserts and queries
c = conn.cursor()


### DATABASE TESTING
c.execute("""CREATE TABLE IF NOT EXISTS awesomepossum(row_id INTEGER PRIMARY KEY, name text NO NULL)""")
c.execute("""INSERT INTO awesomepossum VALUES(NULL, "Billy")""")
print("INSERT BABY")
closeDB(conn);


























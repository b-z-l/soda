import sys
from os import makedirs
from os import path
from os import system
from shutil import copy
from time import sleep
import sqlite3


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
#sleep(1)
print()
print("Data storage path: " + storage_path)
print("Project name: " + project_name)
print()

projectExists = path.exists(project_path)
#sleep(1.5)

if (projectExists):
    print("The " + project_name + " project directory already exists at " + project_path)
    print("If you command you will be importing data into that project.")
else:
    print("Project " + project_name + " does not currently exist")
    print("A new project folder will be created at " + project_path)
    print("A new database file will be created at " + database_path)

sleep(1.5)
print()
command = ""
while (command != "yes" and command != "no"):
    command = input("Are you sure you want to continue (yes or no)? ")

if (command == "no"):
    print("OK! Quitting...")
    sys.exit()
if (not projectExists):
    newProject()

def newProject():
    print("Creating new directory " + project_path, end="")
    try:
        makedirs(project_path)
    except Exception as e:
        print("Error: Couldn't create new directory")
        print(e)
        sys.exit()
    print("Directory created.")
























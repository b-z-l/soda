# SODA: Small Sensor Organizing Database Application

## How This Works

SODA waits for a new volume to be inserted into the computer (SD card, USB stick, hard drive, etc). It scans the filenames of the drive for files which include the string "SENSOR". It then parses the filename for the year and month the log file was created, it checks if that file exists in the project directory, if it doesn't exist, SODA will copy the file into the project directory specified by the user, and import its data into the database.

## Important Files

### Config.py

This file contains two important variables which you should set.

##### PROJECT_NAME
 
This is the name of the project we are currently working on. It determines the name of the directory where the project files will be saved, and the database file in that folder will take this name.

##### PROJECT_DIRECTORY

This is the directory where all project folders are created. This could be something like 'C:\\Users\\JoeUser\\Dropbox\\Small-Sensors\\'

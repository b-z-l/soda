# SODA: Small Sensor Organizing Database Application

This application waits for drives to be interted, 

## How This Works

SODA waits for a new volume to be inserted into the computer (SD card, USB stick, hard drive, etc). It scans the filenames of the drive for files which include the string "SENSOR". It then parses the filename for the year and month the log file was created, it checks if that file exists in the project directory, if it doesn't exist, SODA will copy the file into the project directory specified by the user, and import its data into the database.

## Important Files

### Config.py

This file contains two important variables which you should set.

##### PROJECT_NAME
 
This is the name of the project we are currently working on. It determines the name of the directory where the project files will be saved, and the database file in that folder will take this name.

##### PROJECT_DIRECTORY

This is the directory where all project folders are created. This could be something like 'C:\\Users\\JoeUser\\Dropbox\\Small-Sensors\\'

### Schema.py

Schema.py is read in by SODA to create a database on its first run in a new project directory. It defines three tables in the database.

<table style="width:100%">
  <tr>
    <th>locations</th>
    <th>sensors</th> 
    <th>sensor_datas</th>
  </tr>
  <tr>
    <td>Jill</td>
    <td>Smith</td> 
    <td>50</td>
  </tr>
  <tr>
    <td>Eve</td>
    <td>Jackson</td> 
    <td>94</td>
  </tr>
</table>

locations        sensors          sensor_datas
----------       ---------        --------------
location_id      date             temperature
location         sensor_id        humidity
                 arduino_id       PM25_x
                 datashield_id    PM25_y
                 sdcard_id        co_ppm
                 shinyei_id       co_v
                 o3_sensor_id     o3_ppb
                 co_sensor_id     o3_v
                 dht22_id         sensor_id
                                  location_id
                                  datetime
   
                                  
####### NOTE: SODA reads data from the sensor file IN THE SAME ORDER IT IS ORGANIZED IN THE DATABASE. The order of the configuration is less importan
                                  
 

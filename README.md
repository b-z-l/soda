# SODA: Small Sensor Organizing Database Application

SODA waits for a new volume to be inserted into the computer (SD card, USB stick, hard drive, etc)., and scans the files on that volume for sensor files with the format:

 YYYY-MM-DD_HHhMMm_SENSOR000.txt
 
Files are identified by looking for 'SENSOR' in the filename then parses the name for the year and month the log file was created, it checks if that file exists in the project directory, if it doesn't exist, SODA will copy the file into the project directory specified by the user, and import its data into the database. If files are found with the same name, it won't try and import the data again.

## Notes

The header is parsed by the application. The character # leads all lines of the file header. Don't change stuff around, things will not work.

### Depedencies

SODA relies on another application to eject volumes automagically when we are done importing data. The application can be downloaded here: HTTP://www.JSDFSKLDFJ.COM and should do in the directory with the other SODA files.

### So, you want to change parts on a particular sensor?



## Project Files

### Config.py

This file contains two important variables which you should set.

##### PROJECT_NAME
 
This is the name of the project we are currently working on. It determines the name of the directory where the project files will be saved, and the database file in that folder will take this name.
  
  </tr>
  <tr>
    <td>location_id</td>
    <td>sensor_id</td> 
    <td>temperature</td>
  </tr>
  <tr>
    <td>location</td>
    <td>arduino_id</td> 
    <td>humidity</td>
  </tr>
    <tr>
    <td></td>
    <td>datashield_id</td> 
    <td>PM25_x</td>
  </tr>
    <tr>
    <td></td>
    <td>sdcard_id</td> 
    <td>PM25_y</td>
  </tr>
    <tr>
    <td></td>
    <td>shinyei_id</td> 
    <td>co_ppm</td>
  </tr>
    <tr>
    <td></td>
    <td>o3_sensor_id</td> 
    <td>co_v</td>
  </tr>
    <tr>
    <td></td>
    <td>co_sensor_id</td> 
    <td>o3_ppb</td>
  </tr>
    <tr>
    <td></td>
    <td>dht22_id</td> 
    <td>o3_v</td>
  </tr>
    <tr>
    <td></td>
    <td>date</td> 
    <td>sensor_id</td>
  </tr>
    <tr>
    <td></td>
    <td></td> 
    <td>location_id</td>
  </tr>
    <tr>
    <td></td>
    <td></td> 
    <td>datetime</td>
  </tr>
</table>
  
### Soda.py
  
This is the primary application flow.
  
### App.py
  
This holds the meat of the application, routines which are called from Soda.py.
      
                              

                                  
 

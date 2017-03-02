schema = ['''CREATE TABLE locations (
		id INTEGER PRIMARY KEY,
		location TEXT NOT NULL)'''
	,
	'''CREATE TABLE sensors (
		date TEXT,
		sensor_id INTEGER,
		enclosure_id INTEGER,
		arduino_id INTEGER,
		datashield_id INTEGER,
		sdcard_id INTEGER,
		shinyei_id INTEGER,
		o3_sensor_id INTEGER,
		co_sensor_id INTEGER,
		dht22_id INTEGER,
		PRIMARY KEY (date, sensor_id))'''
	,
	'''CREATE TABLE sensor_datas (
		temperature REAL,
		humidity REAL,
		pm25_x REAL,
		pm25_y REAL,
		co_ppm REAL,
		co_v REAL,
		o3_ppb REAL,
		o3_v REAL,
		sensor_id INTEGER,
		location_id INTEGER,
		datetime TEXT,
		FOREIGN KEY(sensor_id) REFERENCES sensors(id),
		FOREIGN KEY(location_id) REFERENCES locations(id),
		PRIMARY KEY (sensor_id, location_id, datetime))'''
]

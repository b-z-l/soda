#include <EEPROM.h>

unsigned long sampleInterval = 15000;
long maxSamples = EEPROM.length() / sizeof(dataObject);

// read, don't write (or overwrite!) data by default
boolean recordMode = false;

int ledPin = 13;

// button stuff
int buttonPin = 2;
volatile unsigned long lastPushTime = 0;
volatile unsigned long elapsed;
volatile boolean buttonActuated = false;

// button ISR
void buttonPress() {
	if (millis() - lastPushTime > 200) {
		buttonActuated = true;
		elapsed = millis() - lastPushTime;
		lastPushTime = millis();
	}
}

struct dataObject {
	float time;
	float temp;
	char words[10];
};

void setup() {	
	Serial.begin(9600);
	float startTime = millis();
}

void loop() {

	//lets hang out for 5 seconds before we start returning data by default
	while ( millis() - startTime <= 5000) {
		if (buttonActuated) {
			unsigned long holdStart = millis();
			while (!digitalRead(2)) {}
			unsigned long holdTime = millis() - holdStart;
			// if button is held for 5 seconds, we are going to write data!
			if (holdTime >= 5000) {
				blink(5);
				recordMode = true;
			}
		}
	}

	if (recordMode == false) {
		Serial.print("(r) recall (e) erase: ");
		while (Serial.available() < 1) {}
		int command = Serial.read();

		if ((char)command = 'r') {
			recallData();
		}
		else if ((char)command = 'e') {
			eraseData();
		}

	else {
		recordData();
	}
}

void recallData() {
	int eeAddress= 0;
	for (int i = 0; i < maxSamples; i++) {
		dataObject reading;
		EEPROM.get(eeAddress, reading);
		Serial.print(reading.time);
		Serial.print(", ");
		Serial.print(reading.temp);
		Serial.print(", ");
		Serial.println(reading.words);
		eeAddress = eeAddress + sizeof(reading);
	}
}

void recordData() {
	int eeAddress= 0;
	for (int i = 0; i < maxSamples; i++) {
		dataObject reading;
		getReading(*reading);
		EEPROM.put(eeAddress, reading);
		eeAddress = eeAddress + sizeof(reading);
	}
}

void eraseData() {
	for (int i = 0; i < EEPROM.length(); i++) {
		EEPROM.write(i, 0);
	}
}

void blink(int i) {
	for (int j = 0; j < i; j++) {
		digitalWrite(ledPin, LOW);
		delay(500);
		digitalWrite(ledPin, HIGH);
		delay(500);
	}
}

#include <FreeStack.h>
#include <Sdfat.h>


/* Air Sensor Everywhere_v.1
   Small Sensors Group - University of Massachusetts Amherst
   Environmental Health Science - Lab of Richard Peltier
   Implemented by: Filimon Kiros and Benjamin Lazan

   Arduino UNO with Adafruit Sdfat Data Logger Sheild

   Wiring and wire colors

   Digital Pins
   0  - reserved for RX
   1  - reserved for TX
   2  -
   3  - Temp/Humidity - green
   4  - Shinyei PM2.5 -purple
   5  -
   6  -
   7  -
   8  -
   9  -
   10 - reserved for Sdfat
   11 - reserved for Sdfat
   12 - reserved for Sdfat
   13 - reserved for Sdfat (LED power)

   Analog Pins
   AO - CO - yellow
   A1 - O3 - green
   A2 -
   A3 -
   A5 - reserved for RTC
   A6 - reserved for RTC


   Ground Pins
   CO - brown
   O3 - black
   PM sensor - white
   Temp/Rh - black

   Power Pins
   CO - 5V -red
   O3 - 5V -orange
   PM sensor - 5V - purple
   Temp/Humid - 3.3V - red


   Notes:

   Shinyei Wiring:
                     Front of Unit (10K Ohm resisitor connecting GND to Pin 1)
                     This makes P2 more sensitive (REF: https://indiaairquality.com/2016/07/24/circuit-diagram-for-the-42r/)
                     Take reading from P2 channel only.

    pin    1       2       3      4       5
    use    empty   P1      5V      P2      GND
    color                  purple  grey    white

   Real Time Clock:
     To calibrate an Adafruit Sdfat logger RTC, one must
     install a battery on the Sdfat shield, Download the
     Adafruit RTClib library, and run the ds1307 example
     sketch before loading this air sensor software

*/
#include <SPI.h>
#include <SoftwareSerial.h>
#include <DHT22.h>
#include <Wire.h>
#include "RTClib.h"
#include <avr/sleep.h>
#include <avr/power.h>
#include <avr/wdt.h>

//
// So you want to change a component?
//
// Then the corresponding component ID number below may be changed,
// and the config_date value should be updated in the format YYYY-MM-DD
// This new configuration will be recorded into the database.
char config_date[12] =  "2017-02-20";
int sensor_id =           1;
int enclosure_id =        1;
int arduino_id =          1;
int datashield_id =       1;
int sdcard_id =           1;
int shinyei_id =          1;
int o3_sensor_id =        1;
int co_sensor_id =        1;
int dht22_id =            1;

// logging options
#define LOG_INTERVAL 2000
#define LOG_TO_SERIAL true

// sleep and wake settings in milliseconds
// e.g. 1 hour = 3600000
#define WAKE_DURATION    5400000    //2hrs = 7200000 ms
#define SLEEP_DURATION   2700000   //30min = 1800000 ms

#define MAX_SLEEP_ITERATIONS   SLEEP_DURATION / 8000
int sleepIterations = MAX_SLEEP_ITERATIONS;

// RTC object
RTC_PCF8523 RTC;

// Set sd pin
#define chipSelect 10
#define ledPin 13
SdFat sd;
SdFile logfile;


// DHT-22 Temp and Humidity
#define DHTPIN 3
DHT22 myDHT22(DHTPIN);

// Gas sensor settings

enum Gases { CO, O3 };

// Analog read pins
#define CO_PIN 0
#define O3_PIN 1
// Shenyei PM variables
#define PM_P2_PIN 4

unsigned long duration;
unsigned long starttime;
unsigned long sampletime_ms = 300000;   //300sec or 5min
unsigned long lowpulseoccupancy = 0;
float ratio = 0;
float concentration = 0;

float PM25count;
float PM25conc;

uint32_t timer = millis();
uint32_t lastSleepCycle = millis();

volatile bool watchdogActivated = false;

void setup() {
  // for Leonardos, if you want to debug sd issues, uncomment this line
  // to see serial output
  //while (!Serial);

#if LOG_TO_SERIAL
  Serial.begin(9600);
#endif

  Wire.begin();

  if (!RTC.begin())
    logfile.println("RTC failed");

  pinMode(ledPin, OUTPUT);

  // make sure that the default chip select pin is set to
  // output, even if you don't use it:
  pinMode(10, OUTPUT);

  // see if the card is present and can be initialized:
  if (!sd.begin(chipSelect)) {      // if you're using an UNO, you can use this line instead
#if LOG_TO_SERIAL
    Serial.println("Card init. failed!");
#endif
    error(2);
  }

  // this creates file with the format 2017_1_23_20h32m_SENSOR001.txt
  // time on file is set when arduino starts up
  DateTime now = RTC.now();
  int month = now.month();
  int day = now.day();
  int year = now.year();
  int hour = now.hour();
  int minute = now.minute();
  char filename[35] = "";
  sprintf(filename, "%.4d-%.2d-%.2d_%.2dh%.2dm_SENSOR%.3d.txt",
          year % 10000, month % 100, day % 100, hour % 100, minute % 100, sensor_id);
//  logfile = sd.open(filename, FILE_WRITE);

  if (!logfile.open(filename, O_RDWR | O_CREAT | O_AT_END)) {
    sd.errorHalt("opening file for write failed");
  }
  // use the error() function to flash the LED forever on failure
 /* if ( ! logfile ) {
#if LOG_TO_SERIAL
    Serial.print("Couldnt create ");
    Serial.println(filename);
#endif
    error(1);
  }
*/
#if LOG_TO_SERIAL
  Serial.print("Writing to ");
  Serial.println(filename);
#endif

  // flashing LED indicated success in writing to sd file
  for (int i = 0; i < 5; i++) {
    digitalWrite(ledPin, HIGH);
    delay(200);
    digitalWrite(ledPin, LOW);
    delay(200);
  }

  // Set PM pins
  pinMode(PM_P2_PIN, INPUT);

  starttime = millis();

  // Watchdog timer setup for waking from sleep

  // This next section of code is timing critical, so interrupts are disabled.
  // See more details of how to change the watchdog in the ATmega328P datasheet
  // around page 50, Watchdog Timer.
  noInterrupts();

  // Set the watchdog reset bit in the MCU status register to 0.
  MCUSR &= ~(1 << WDRF);

  // Set WDCE and WDE bits in the watchdog control register.
  WDTCSR |= (1 << WDCE) | (1 << WDE);

  // Set watchdog clock prescaler bits to a value of 8 seconds.
  WDTCSR = (1 << WDP0) | (1 << WDP3);

  // Enable watchdog as interrupt only (no reset).
  WDTCSR |= (1 << WDIE);

  // Enable interrupts again.
  interrupts();


  // FILE HEADERS
  // Please don't change the file headers if you intend to load the datas into
  // the database, using the database program. It relies on them to stay
  // juuuust as they are. -Ben

  logfile.print("# ");
  logfile.println(filename);
  logfile.println("# ");

  // Sensor configuration header
  // This information is read into the database to store the current
  // sensor component configuration.
  logfile.println("# Sensor Configuration:");
  logfile.print("# config_date: "); logfile.println(config_date);
  logfile.print("# sensor_id: "); logfile.println(sensor_id);
  logfile.print("# enclosure_id: "); logfile.println(enclosure_id);
  logfile.print("# arduino_id: "); logfile.println(arduino_id);
  logfile.print("# datashield_id: "); logfile.println(datashield_id);
  logfile.print("# sdcard_id: "); logfile.println(sdcard_id);
  logfile.print("# shinyei_id: "); logfile.println(shinyei_id);
  logfile.print("# o3_sensor_id: "); logfile.println(o3_sensor_id);
  logfile.print("# co_sensor_id: "); logfile.println(co_sensor_id);
  logfile.print("# dht22_id: "); logfile.println(dht22_id);
  logfile.print("# If you swap parts record the new component ID and new configuration date in the file SENSORHERE.ino");
  logfile.println("DATE/TIME,TEMP(degC),HUMID(%),PM2.5_ug/m3,PM2.5_#/0.01ft3,CO_PPM,CO_V,O3_PPB,O3_V");

#if LOG_TO_SERIAL
  Serial.print("# ");
  Serial.println(filename);
  Serial.println("# ");
  Serial.print("# config_date: "); Serial.println(config_date);
  Serial.print("# sensor_id: "); Serial.println(sensor_id);
  Serial.print("# enclosure_id: "); Serial.println(enclosure_id);
  Serial.print("# arduino_id: "); Serial.println(arduino_id);
  Serial.print("# datashield_id: "); Serial.println(datashield_id);
  Serial.print("# sdcard_id: "); Serial.println(sdcard_id);
  Serial.print("# shinyei_id: "); Serial.println(shinyei_id);
  Serial.print("# o3_sensor_id: "); Serial.println(o3_sensor_id);
  Serial.print("# co_sensor_id: "); Serial.println(co_sensor_id);
  Serial.print("# dht22_id: "); Serial.println(dht22_id);
  Serial.println("# If you swap parts record the new component ID and new configuration date in the file SENSORHERE.ino");
  Serial.println("# TEMP(degC), HUMID(%), PM2.5_ug/m3, PM2.5_#/0.01ft3, CO_PPM, CO_V, O3_PPB, O3_V, YYYY-MM-DD HH:MM:SS");

#endif
}

void loop() {
  // Don't do anything unless the watchdog timer interrupt has fired.
  if (watchdogActivated)
  {
    watchdogActivated = false;
    // Increase the count of sleep iterations and take a sensor
    // reading once the max number of iterations has been hit.
    sleepIterations += 1;
    if (sleepIterations >= MAX_SLEEP_ITERATIONS) {
      // Reset the number of sleep iterations.
      sleepIterations = 0;

      // reset lastSleepCycle if it wraps around
      if (lastSleepCycle > millis())  lastSleepCycle = millis();  //  a chunk command including no2 deleted here

      // Log sensor readings umtil WAKE_DURATION has ellapsed, don't delete this Filimon!
      while (millis() - lastSleepCycle < WAKE_DURATION) {
        logSensorReadings();
      }

    }
    // Go to sleep!
    sleep();
    lastSleepCycle = millis();

  }
}

void logSensorReadings() {
  // if millis() or timer wraps around, we'll just reset it
  if (timer > millis())  timer = millis();

  // run Shinyei PM calculations
  calculatePM();

  // log data if LOGINTERVAL has elapsed
  if (millis() - timer > LOG_INTERVAL) {
    timer = millis(); // reset the timer

    // fetch the time
    DateTime now;
    now = RTC.now();

    // print date
    logfile.print(now.year(), DEC); logfile.print("-");
    logfile.print(now.month(), DEC); logfile.print('-');
    logfile.print(now.day(), DEC); logfile.print(" ");
    // print time
    logfile.print(now.hour(), DEC); logfile.print(':');
    logfile.print(now.minute(), DEC); logfile.print(':');
    logfile.print(now.second(), DEC); logfile.print(", ");
#if LOG_TO_SERIAL
    // print date
    Serial.print(now.year(), DEC); Serial.print("-");
    Serial.print(now.month(), DEC); Serial.print('-');
    Serial.print(now.day(), DEC); Serial.print(" ");
    // print time
    Serial.print(now.hour(), DEC); Serial.print(':');
    Serial.print(now.minute(), DEC); Serial.print(": ");
    Serial.print(now.second(), DEC); Serial.print(", ");
#endif

    // print temperature and humidity
    DHT22_ERROR_t errorCode;
    errorCode = myDHT22.readData();

    logfile.print(myDHT22.getTemperatureC()); logfile.print(", ");
    logfile.print(myDHT22.getHumidity()); logfile.print(", ");
#if LOG_TO_SERIAL
    Serial.print(myDHT22.getTemperatureC()); Serial.print(", ");
    Serial.print(myDHT22.getHumidity()); Serial.print(", ");
#endif

    // Shinyei PM readings....EQUATION DIFFERENT FOR EACH SENSOR
    logfile.print(PM25conc);
    logfile.print(", "); logfile.print(PM25count);
    logfile.print(", ");

#if LOG_TO_SERIAL
    Serial.print(PM25conc);
    Serial.print(", "); Serial.print(PM25count);
    Serial.print(", ");
#endif

    // read gas sensors

    // print CO PPM(Voltage)
    logfile.print(calculateGas(CO));
    logfile.print(", "); logfile.print(readVoltage(CO_PIN));
    logfile.print(", ");

    // print O3 PPM(Voltage)
    logfile.print(calculateGas(O3));
    logfile.print(", "); logfile.print(readVoltage(O3_PIN));
    logfile.println();

#if LOG_TO_SERIAL
    // print CO PPM(Voltage)
    Serial.print(calculateGas(CO));
    Serial.print(", "); Serial.print(readVoltage(CO_PIN));
    Serial.print(", ");

    // print O3 PPM(Voltage)
    Serial.print(calculateGas(O3));
    Serial.print(", "); Serial.print(readVoltage(O3_PIN));
    Serial.println();
#endif

    // write to sd card
    logfile.flush();
  }
}


// blink out an error code
void error(uint8_t errno) {
  while (1) {
    delay(1800);
    for (int i = 0; i < 10; i++) {
      digitalWrite(ledPin, HIGH);
      delay(50);
      digitalWrite(ledPin, LOW);
      delay(50);
    }
  }
}
// calcualteGas()
// caculate gas performs ppm/ppb conversions on raw data
// input: gasVoltage - integer analogRead from MICS sensor
//
// To add a gas you must add the gas to the enum Gases variable
// in the gas settings section, you must add a case to the switch
// statement below which returns a result, it is good practice to add a #define statement
// to assign the analog pin number to a variable which can be easily
// changed if needed. e.g.
//                  #define NO2_PIN 9

float calculateGas(int gas) {
  float result;
  float voltage;             // v has significant decimals
  switch (gas) {

    case CO:
      voltage = readVoltage(CO_PIN);
      result = ((22.199 * voltage) - 16.394);              // CO_4 (1-00044) calibration equation (linear upto 2.64 v)
      if (result < 0)
        result = 0;
      return result;
      break;

    case O3:
      voltage = readVoltage(O3_PIN);
      result = (176.75 * pow(2.71828, (-0.806 * voltage)));                // O3_4 (1-00034) calibration equation (exponential)
      if (result < 0)
        result = 0;
      return result;
      break;

  }
}

// calculatePM()
// This function runs in the main loop every millisecond,
// concentration and particle count are only calculated when
// sampletime_ms has elapsed, sampletime_ms can be adjusted in the
// PM variables section towards the top of this file

void calculatePM() {

  duration = pulseIn(PM_P2_PIN, LOW);
  lowpulseoccupancy = lowpulseoccupancy + duration;

  if ((millis() - starttime) > sampletime_ms) {
    ratio = lowpulseoccupancy / (sampletime_ms * 10.0);
    PM25count = 1.1 * pow(ratio, 3) - 3.8 * pow(ratio, 2) + 520 * ratio + 0.62;
    // PM2.5 count (#/0.01ft3) to mass concentration (ug/m3) conversion
    PM25conc = (0.2425 * pow(PM25count, 0.7726));                 // Shinyie_4 Equation (power function)
    lowpulseoccupancy = 0;
    starttime = millis();
  }
}

float readVoltage(int PIN) {
  return (analogRead(PIN) * (5.0 / 1023));
}


// Define watchdog timer interrupt.
ISR(WDT_vect)
{
  // Set the watchdog activated flag.
  // Note that you shouldn't do much work inside an interrupt handler.
  watchdogActivated = true;
}

// Put the Arduino to sleep.
void sleep()
{
  // Set sleep to full power down.  Only external interrupts or
  // the watchdog timer can wake the CPU!
  set_sleep_mode(SLEEP_MODE_PWR_DOWN);

  // Turn off the ADC while asleep.
  power_adc_disable();

  // Enable sleep and enter sleep mode.
  sleep_mode();

  // CPU is now asleep and program execution completely halts!
  // Once awake, execution will resume at this point.

  // When awake, disable sleep mode and turn on all devices.
  sleep_disable();
  power_all_enable();
}




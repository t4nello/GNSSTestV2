#include <SPI.h>
#include <ESP8266WiFi.h>
#include <MQTT.h>
#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>
#include <ArduinoJson.h>
#include <TimeLib.h>

#undef  MQTT_MAX_PACKET_SIZE 
#define MQTT_MAX_PACKET_SIZE 500 
#define RxPin 4
#define txPin 5
#define baudRate 115200
#define GPSBaud 9600
#define LED_BUILTIN 2

const char ssid[] = "Woz_operacyjny_ABW";
const char pass[] = "PiwkoPaliwko123!";

TinyGPSPlus gps;
SoftwareSerial ss(RxPin, txPin);
WiFiClient net;
MQTTClient client(256);

unsigned long lastMillis = 0;
bool enableGps = false;

void connect() {

  while (WiFi.status() != WL_CONNECTED) {
   Serial.print(".");
  }

  Serial.print("\nconnecting...");
  while (!client.connect((WiFi.macAddress().c_str()), "public", "public")) {
   Serial.print(".");
  }

  client.publish("esp/connection/connected", WiFi.macAddress());
  client.subscribe("esp/detect");
  client.subscribe("esp/heartbeat/receive");
  client.subscribe("gps/metric/enable");
  client.subscribe("gps/metric/disable");
}

int SessionId=0;
void messageReceived(String &topic, String &payload) {

  if (topic.compareTo("esp/detect") == 0 && payload.compareTo(WiFi.macAddress()) == 0) {
     digitalWrite(LED_BUILTIN, LOW);
     delay(100);
     digitalWrite(LED_BUILTIN, HIGH);    
  } else if (topic.compareTo("gps/metric/enable") == 0) {
    SessionId = payload.toInt();
    if (SessionId == 0){
    enableGps = false;
    }
    else
    enableGps = true;
    
   
  } else if (topic.compareTo("gps/metric/disable") == 0) {
    enableGps = false;
  }
  else if (topic.compareTo("esp/heartbeat/receive") == 0)
    client.publish("esp/heartbeat/send", WiFi.macAddress());
}

long convertGPSDateTime() {
        int year = gps.date.year();
        int month = gps.date.month();
        int day = gps.date.day();
        int hour = gps.time.hour();
        int minute = gps.time.minute();
        int second = gps.time.second();

       
        tmElements_t tm;
        tm.Year = year - 1970; 
        tm.Month = month;
        tm.Day = day;
        tm.Hour = hour;
        tm.Minute = minute;
        tm.Second = second;
        time_t timestamp = makeTime(tm);
     return timestamp;
}

void publishInfo() {
    float latitude = gps.location.lat();
    float longitude = gps.location.lng();

    char latitudeBuffer[16];
    char longitudeBuffer[16];
    dtostrf(latitude, 8, 6, latitudeBuffer);
    dtostrf(longitude, 8, 6, longitudeBuffer);
    StaticJsonDocument<1024> doc;
    doc["device"] = WiFi.macAddress();
    doc["latitude"] = atof(latitudeBuffer); 
    doc["longitude"] = atof(longitudeBuffer); 
    doc["speed"] = gps.speed.kmph();
    doc["altitude"] = gps.altitude.meters();
    doc["satellites"] = gps.satellites.value();
    doc["time"] = convertGPSDateTime();
    doc["sessionid"] = SessionId;

    String jsonStr;
    serializeJson(doc, jsonStr);

    client.publish("gps/metric", jsonStr.c_str());
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
  ss.begin(GPSBaud);
  Serial.begin(baudRate);
  WiFi.begin(ssid, pass);
  client.setWill("esp/connection/disconnected",WiFi.macAddress().c_str());
  client.begin("192.168.0.213", net);
  connect();
}

void loop() {

  client.loop();
  delay(10);
  client.onMessage(messageReceived);
  if (!client.connected()) {
  
    connect();
  }
  while (ss.available() > 0)
    if (gps.encode(ss.read()))
    if (gps.location.isValid() && enableGps == true ){
      if (millis() - lastMillis > 7000) {
          publishInfo();
        
          lastMillis = millis();
         
    }
  }
}

#!/bin/sh

# Adres hosta MQTT
MQTT_HOST="192.168.0.213"
# Temat MQTT
MQTT_TOPIC="gps/metric"
# Numer portu MQTT
MQTT_PORT=1883

# Funkcja wysy�aj�ca dane przez MQTT
send_data() {
    # Konstruowanie danych JSON
    PAYLOAD=$(cat <<EOF
{
  "device": "00:1E:42:2B:9C:13",
  "latitude": $1,
  "longitude": $2,
  "speed": $3,
  "altitude": $4,
  "satellites": $5,
  "time": $6,
  "sessionid": $SESSION_ID
}
EOF
)
    # Wys�anie danych przez MQTT
    mosquitto_pub -h $MQTT_HOST -p $MQTT_PORT -t $MQTT_TOPIC -m "$PAYLOAD"
}

# Pocz�tkowy stan parametru enable
ENABLED=0
# Pocz�tkowy numer sesji
SESSION_ID=0

while true; do
    # Sprawdzenie czy parametr enable jest ustawiony
    if [ $ENABLED -eq 0 ]; then
        # Nas�uchiwanie na temacie gps/metric/enable na MQTT
        ENABLED=$(mosquitto_sub -h $MQTT_HOST -p $MQTT_PORT -t "gps/metric/enable" -C 1)
        # Ustawienie numeru sesji
        SESSION_ID=$ENABLED
    else
        # Pobranie danych z GPS
        LATITUDE=$(gpsctl -i)
        LONGITUDE=$(gpsctl -x)
        SPEED=$(gpsctl -v)
        ALTITUDE=$(gpsctl -a)
        SATELLITES=$(gpsctl -p)
        TIME=$(gpsctl -t)
        
        # Wys�anie danych przez MQTT
        send_data $LATITUDE $LONGITUDE $SPEED $ALTITUDE $SATELLITES $TIME
        
        # Oczekiwanie 7 sekund przed kolejnym wys�aniem danych
        sleep 7
    fi
done

#!/bin/sh
#kmod-usb-core_5.10.176-1_mips_24kc.ipk
#kmod-usb-serial-pl2303_5.10.176-1_mips_24kc.ipk
#kmod-usb-serial_5.10.176-1_mips_24kc.ipk
# Ustawienia
mqtt_broker="192.168.0.213"
mqtt_topic_enable="gps/metric/enable"
mqtt_topic_disable="gps/metric/disable"
mqtt_topic_metric="gps/metric"
device_mac="C4:93:00:1A:5D:FD"
session_id=""
gpspipe_command="gpspipe -x 4 --json"



transform_json() {
  input_json=$1
  device=$(echo $input_json | jq -r '.device')
  latitude=$(echo $input_json | jq -r '.lat')
  longitude=$(echo $input_json | jq -r '.lon')
  speed=1
  altitude=$(echo $input_json | jq -r '.alt')
  satellites=4
  timestamp=$(echo $input_json | jq -r '.time')
  time=$(date -u +'%s')


  transformed_json="{\"device\":\"$device_mac\",\"latitude\":$latitude,\"longitude\":$longitude,\"speed\":$speed,\"altitude\":$altitude,\"satellites\":$satellites,\"time\":$time,\"sessionid\":$session_id}"

  echo $transformed_json
}

# Początkowe ustawienia
gps_enabled=false

# Nasłuchuj temat gps/metric/enable
mosquitto_sub -h $mqtt_broker -t $mqtt_topic_enable | while read message; do
  if [ "$gps_enabled" == "false" ]; then
    gps_enabled=true
    echo "GPS measurements enabled. Session ID: $message"
    session_id=$message
    # Rozpocznij pomiar i wysyłaj dane
    while [ "$gps_enabled" == "true" ]; do
      gps_data=$(eval $gpspipe_command | sed -n '/TPV/{p;q}')
      transformed_data=$(transform_json "$gps_data")
      mosquitto_pub -h $mqtt_broker -t $mqtt_topic_metric -m "$transformed_data"
      sleep 4  # Odczekaj 5 sekund, dostosuj do potrzeb
    done
  fi
done &

# Nasłuchuj temat gps/metric/disable
mosquitto_sub -h $mqtt_broker -t $mqtt_topic_disable | while read message; do
  if [ "$gps_enabled" == "true" ]; then
    gps_enabled=false
    echo "GPS measurements disabled. Session ID: $session_id"
  fi
done

# Zakończ procesy nasłuchujące
kill $(jobs -p)

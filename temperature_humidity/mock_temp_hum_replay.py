#!/usr/bin/python3
# encoding=utf-8

import paho.mqtt.client as mqtt
import logging
import time
import sys
import json
import csv
import random
import signal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

SERVER = 'localhost'
PORT = 1883
USERNAME = None
PASSWORD = None

SENSOR_NAME = "temperature_a"
SENSOR_ID = 'temperature_a'
UNITS = 'ºC'
CLIENT_ID = f"sensor/{SENSOR_NAME}"
connected = False

done = False

def exit(signalNumber, frame):  
    global done
    done = True
    return


def on_connect(mqttc, obj, flags, rc):
    global connected
    connected = True

    logger.info(f"Connected to {mqttc._host}:{mqttc._port}")

    mqttc.publish(f"{CLIENT_ID}/status", 'online', retain=True)
    for t in ["humidity", "temperature"]: 
        for i in range(4):
            # HA AUTOCONFIG
            mqttc.publish(f'homeassistant/sensor/{t}_{i+1}/config', json.dumps({
                'name': f"{t}_{i+1}",
                'availability_topic': f'{CLIENT_ID}/status',  # Online, Offline
                'device_class': t,
                'unit_of_measurement': 'ºC' if t == 'temperature' else '%',
                'unique_id': f"{t}_{i+1}",
                'state_topic': f'{t}_{i+1}/state',  # Value published
                'force_update': True}), retain=True)

    return True


def on_message(mqttc, obj, msg):
    logger.info(f"{msg.topic} {str(msg.qos)} {str(msg.payload)}")


def loop(mqttc):
    logger.info("Loop start")

    while not done:
        if not connected:
            logger.info("Not Connected")
        else:

            with open(sys.argv[1], 'r') as f:
                reader = csv.reader(f)
                
                tmock = 0
                #2, 1458031648645, 1, 4, 20.73, 39.983, 214.29, 657.8, 0, 0, 0, 0
                for row in reader:
                    logger.info(row)
                    rel_time = int(row[2])
                    if rel_time > tmock:
                        time.sleep((rel_time - tmock) *10)
                    tmock = rel_time
                    sid = row[3].strip()

                    logger.info(f"temperature_{sid}/state")
                    offset = 0
                    if sid == "4":
                        offset = -8
                    elif sid== "3":
                        offset = -1.3
                    mqttc.publish(f"temperature_{sid}/state", round(float(row[4])+offset + (0.5-random.random())/5,2), retain=True)
                    
                    offset = 0
                    if sid == "4":
                        offset = -12
                    elif sid== "3":
                        offset = 6.3 

                    mqttc.publish(f"humidity_{sid}/state", round(float(row[5])+offset + (0.5-random.random()),2), retain=True)

        time.sleep(10)

    return True


def main():
    signal.signal(signal.SIGINT, exit)

    mqttc = mqtt.Client(client_id='clients/' + CLIENT_ID)
    mqttc.will_set(f"{CLIENT_ID}/status", 'offline', retain=True)

    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    if USERNAME is not None:
	    mqttc.username_pw_set(username=USERNAME, password=PASSWORD)

    mqttc.loop_start()

    logger.info("Connecting to MQTT")
    mqttc.connect(host=SERVER, port=PORT, keepalive=60)

    logger.info("Running")

    while not done:
        try:
            if not loop(mqttc):
                mqttc.disconnect()
                break
        except:
            logger.exception("")
            time.sleep(10)


if __name__ == '__main__':
    main()


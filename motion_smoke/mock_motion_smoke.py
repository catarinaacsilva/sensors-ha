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
import argparse

dataset = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

SERVER = 'localhost'
PORT = 1883
USERNAME = None
PASSWORD = None

SENSOR_NAME = "motion_a"
SENSOR_ID = 'motion_a'
UNITS = 'PPM'
CLIENT_ID = f"sensor/{SENSOR_NAME}"
connected = False

done = False

def exit(signalNumber, frame):  
    global done
    done = True
    return


def on_connect(mqttc, obj, flags, rc):
    global connected

    mqttc.publish(f"{CLIENT_ID}/status", 'online', retain=True)
    for t in ['motion', 'smoke']: 
        logger.info(t)
        for i in range(3):
            logger.info(i)
            # HA AUTOCONFIG
            msg = json.dumps({
                'name': f"{t}_{i+1}",
                'availability_topic': f'{CLIENT_ID}/status',  # Online, Offline
                'device_class': 'motion' if t == 'motion' else 'smoke',
                'unit_of_measurement': '' if t == 'motion' else '',
                'unique_id': f"{t}_{i+1}",
                'state_topic': f'{t}_{i+1}/state',  # Value published
                'force_update': True})
            logger.info(msg)
            mqttc.publish(f'homeassistant/sensor/{t}_{i+1}/config', msg, retain=True)
    
    logger.info(f"Connected to {mqttc._host}:{mqttc._port}")
    connected = True

    return True


def on_message(mqttc, obj, msg):
    logger.info(f"{msg.topic} {str(msg.qos)} {str(msg.payload)}")


def loop(mqttc):
    logger.info("Loop start")

    while not done:
        if not connected:
            logger.info("Not Connected")
        else:

            with open(dataset, 'r') as f:
                reader = csv.reader(f)
                
                tmock = 0
                
                for row in reader:
                    logger.info(row)
                    
                    rel_time = int(float(row[0]))
                    if tmock == 0:
                        tmock = rel_time
                    if rel_time > tmock:
                        time.sleep((rel_time - tmock) *10)
                    tmock = rel_time
                    sid = row[1].strip()

                    if sid == 'b8:27:eb:bf:9d:51':
                        sid = 1
                    elif sid == '00:0f:00:70:91:0a':
                        sid = 2
                    else:
                        sid = 3

                    #value = 1.0 if row[7] >= 0 else 0.0
                    value = round(float(row[7]) + (0.5-random.random())/5,4)
                    logger.info(f"smoke_{sid}/state = {value}")
                    mqttc.publish(f"smoke_{sid}/state", value, retain=True)
                    
                    value = 1.0 if bool(row[6]) == True else 0.0
                    logger.info(f"motion_{sid}/state = {value}")
                    mqttc.publish(f"motion_{sid}/state", value , retain=True)

        time.sleep(10)

    return True


def main(args):
    signal.signal(signal.SIGINT, exit)

    global dataset
    dataset = args.d

    mqttc = mqtt.Client(client_id='clients/' + CLIENT_ID)
    mqttc.will_set(f"{CLIENT_ID}/status", 'offline', retain=True)

    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    if USERNAME is not None:
	    mqttc.username_pw_set(username=USERNAME, password=PASSWORD)

    mqttc.loop_start()

    logger.info("Connecting to MQTT")
    mqttc.connect(host=args.u, port=args.p, keepalive=60)

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
    parser = argparse.ArgumentParser(description='Virtual Sensores HA')
    parser.add_argument('-u', type=str, help='MQTT URL', default='localhost')
    parser.add_argument('-p', type=int, help='MQTT Port', default=1883)
    parser.add_argument('-d', type=str, help='Sensor Dataset', default='iot_telemetry_data.csv')
    
    args = parser.parse_args()
    main(args)


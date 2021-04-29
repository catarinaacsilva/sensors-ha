#!/usr/bin/python3
# encoding=utf-8

import paho.mqtt.client as mqtt
import logging
import json
import time
import argparse


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


lock = True


def on_connect(client, userdata, flags, rc):  
    logger.debug('Connected with result code {0}'.format(str(rc)))  
    client.subscribe('home-assistant/frontdoor/set', qos=1)
    reply_topic = 'home-assistant/frontdoor/'
    if lock:
        msg = 'LOCK'
    else:
        msg = 'UNLOCK'
    client.publish(reply_topic, msg, qos=1)


def on_message(client, userdata, msg):
    global lock 
    logger.info('Incoming topic: %s', msg.topic)
    
    incoming = msg.payload.decode('utf-8')
    if incoming == 'LOCK':
        lock = True
    elif incoming == 'UNLOCK':
        lock = False
    else:
        logger.warning('Unkown payload: %s', incoming)

    reply_topic = 'home-assistant/frontdoor/'
    
    if lock:
        msg = 'LOCK'
    else:
        msg = 'UNLOCK'
    
    logger.info(msg)
    client.publish(reply_topic, msg.encode(), qos=1)


def main(args):
    client =mqtt.Client('lock')
    
    client.on_connect = on_connect  
    client.on_message = on_message
    client.enable_logger()
    logger.debug('Connect to %s', args.u)
    client.connect(args.u, port=args.p)
    client.loop_start()

    done = False
    while not done:
        time.sleep(1)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Virtual Lock')
    parser.add_argument('-u', type=str, help='MQTT URL', default='192.168.94.98')
    parser.add_argument('-p', type=int, help='MQTT Port', default=1883)
    
    args = parser.parse_args()
    main(args)
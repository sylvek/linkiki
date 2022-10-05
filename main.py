#!/usr/bin/python
import paho.mqtt.client as mqtt
import argparse
import serial
import sys
import errno
import signal
import os
import logging
import time
import linky

linky = linky.Linky()

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='linkiki.log', filemode='w', level=logging.INFO)
logger = logging.getLogger("linkiki")

parser = argparse.ArgumentParser(
    description='fetch data from linky and push it to mqtt')
parser.add_argument('usbport', metavar='usbport',
                    help='usb port like /dev/serial0', nargs='?', default='/dev/serial0')
parser.add_argument('hostname', metavar='hostname',
                    help='hostname of mqtt server', nargs='?', default="0.0.0.0")
parser.add_argument('port', metavar='port',
                    help='port of mqtt server', nargs='?', default="1883")
parser.add_argument('topic1', metavar='topic1', help='topic used to publish power consumption (in wh)',
                    nargs='?', default="sensors/linky/watt")
parser.add_argument('topic2', metavar='topic2',
                    help='topic used to publish state (0 if HC, 1 if HP)',
                    nargs='?', default="sensors/linky/state")
args = parser.parse_args()

usbport = args.usbport
run = True
previousValue = -1
previousState = -1
previousTimestamp = -1
previousValueHCHC = -1
previousValueHCHP = -1


def signal_handler(signal, frame):
    global run
    logger.info("Ending and cleaning up")
    run = False


def handle_debug(signal, frame):
    logger.info("Switching to DEBUG level")
    logger.setLevel(logging.DEBUG)


def handle_info(signal, frame):
    logger.info("Switching to INFO level")
    logger.setLevel(logging.INFO)


try:
    logger.info("Starting listening Linky")
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGUSR1, handle_debug)
    signal.signal(signal.SIGUSR2, handle_info)

    while not os.path.exists(usbport):
        if not run:
            logger.error("Are you sure on %s ?", usbport)
            sys.exit(errno.EIO)
        logger.debug("waiting for %s", usbport)
        time.sleep(2)

    ser = serial.Serial(port=usbport, baudrate=1200, bytesize=serial.SEVENBITS,
                        parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE, timeout=1)

    client = mqtt.Client()
    client.connect(args.hostname, int(args.port), 60)
    logger.info("connected to MQTT broker")
    client.loop_start()
    logger.info("running...")
except Exception as e:
    logger.exception("Fatal error in main loop. %s", e)
    sys.exit(errno.EIO)

while run:
    try:
        lignes = linky.read(ser)

        hchc = int(lignes["HCHC"])
        hchp = int(lignes["HCHP"])

        # we check if we are switching states 0 = hchc / 1 = hchp
        if hchc > previousValueHCHC:
            logger.debug("hchc is increasing: %s", hchc)
            state = 0
            previousValueHCHC = hchc

        if hchp > previousValueHCHP:
            logger.debug("hchp is increasing: %s", hchp)
            state = 1
            previousValueHCHP = hchp

        if previousState != state:
            client.publish(args.topic2, state, retain=True)

        previousState = state

        # we calculate the current power consumption
        newValue = hchc + hchp
        newTimestamp = time.time()
        if newValue != previousValue:
            logger.debug("new value: %s", newValue)
            if previousValue != -1:
                currentConsumption = int(
                    round((newValue - previousValue) /
                          (newTimestamp - previousTimestamp)*3600)
                )
                client.publish(args.topic1, currentConsumption)
            previousValue = newValue
            previousTimestamp = newTimestamp
    except Exception as e:
        logger.exception("error in main loop. %s", e)

ser.close()
client.disconnect()

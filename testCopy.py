import json
import os
import argparse
import asyncio
import subprocess
import time
import sys
from argparse import ArgumentParser
import pathlib
import serial
import sqlite3

from bellows.zigbee.application import ControllerApplication

from csv import DictWriter


async def getZigbeeDevices(args):
    results = {}

    results['TARGET_IPADDR'] = ''
    results['FIRMWARE_VERION'] = 'None'
    results['SCAN_NAME'] = "getZigbeeDevices"
    results['MODEL'] = 'None'
    results['DEVICE_NAME'] = 'None'
    results['NUM_ZIGBEE_ENDPOINTS'] = '0'
    results['SERIAL_DEVICES'] = {}

    try:
        controller = await ControllerApplication.new(
            config = ControllerApplication.SCHEMA({
                "database_path": str(args.Zigbee_db_path),
                "device": {
                    "path": str(args.Zigbee_device_path).rstrip(),
                    "baudrate": 57600
                }
            }),
            auto_form = True,
            start_radio = True,
        )
        
    except (serial.serialutil.SerialException, sqlite3.OperationalError) as err:
        results['SCAN_RESULT'] = -1
        results['SCAN_RESULT_DESC'] = err
        return results

    hub_name, model_name, version = await (controller._ezsp.get_board_info())
   
    results['TARGET_IPADDR'] = ""
    results['FIRMWARE_ID'] = version
    results['MODEL'] = model_name
    results['DEVICE_NAME'] = hub_name
    results['NUM_ZIGBEE_ENDPOINTS'] = len(list(controller.devices.values())) -1
    results['SERIAL_DEVICES'] = {}
    
    for dev in controller.devices.values():
        results['SERIAL_DEVICES'][dev.model] = {'DEVICE_NAME': dev.model, 'PROTOCOL': 'ZigBee',
                                                'MODEL': dev.model, 'VENDOR': dev.manufacturer}
    
    results['SCAN_RESULT'] = 1
    results['SCAN_RESULT_DESCRIPTION'] = "Success"
    
    await controller.shutdown()
    return results


def main():

    arg_parser = argparse.ArgumentParser(description = 'Enter your Zigbee hub serial path, and database file')

    arg_parser.add_argument("Zigbee_device_path", type=pathlib.Path,
                            help="Device path of Z-Stick, /dev/tty...")
    arg_parser.add_argument("Zigbee_db_path", type=pathlib.Path,
                            help="Device path of Z-Stick, /dev/tty...")

    args = arg_parser.parse_args()

    test = subprocess.run(['fuser', str(args.Zigbee_device_path)], capture_output=True)
    results = {}
    results['TARGET_IPADDR'] = ''
    results['FIRMWARE_VERION'] = 'None'
    results['SCAN_NAME'] = "getZigbeeDevices"
    results['MODEL'] = 'None'
    results['DEVICE_NAME'] = 'None'
    results['NUM_ZIGBEE_ENDPOINTS'] = '0'
    results['SERIAL_DEVICES'] = {}
    
    if test.stdout != b'':
        results['SCAN_RESULT'] = -1
        results['SCAN_RESULT_DESC'] = "Zigbee Hub is busy"
        print(results)
        return
    
    results = asyncio.run(getZigbeeDevices(args))
    #results = loop.run_until_complete(coroutine)
    print(results)
    #os._exit(os.EX_OK)
    return
    
def getTest():
    print("test")

if __name__ == '__main__':
    main()

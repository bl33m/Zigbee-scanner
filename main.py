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

arg_parser = argparse.ArgumentParser(description = 'Enter your Zigbee hub serial path, and database file')

#   arg_parser = argparse.ArgumentParser("Zigbee_device_path", type=pathlib.Path,
#                                    help="Device path of Z-Stick, /dev/tty...")
args = arg_parser.parse_args()


async def getZigbeeDevices():

    results = dict.fromkeys(['TARGET_IPADDR', 'SCAN_NAME', 'MODEL', 'VENDOR', 'SCAN_RESULT', 'SCAN_RESULT_DESC'])

    try:
        controller = await ControllerApplication.new(
            config = ControllerApplication.SCHEMA({
                "database_path": "/home/bl33m/.config/bellows/app.db",
                "device": {
                    "path": "/dev/ttyUSB1",
                    "baudrate": 57600
                }
            }),
            auto_form = True,
            start_radio = True,
        )

    except (serial.serialutil.SerialException, sqlite3.OperationalError) as err:
        print(f"{err}")
        results['SCAN_RESULT'] = -1
        results['SCAN_RESULT_DESC'] = "No hub found on specificed serial path"
        return results

    for dev in controller.devices.values():
        print(f"Model : {dev.model}")
        print(f"Manufacturer : {dev.manufacturer}")
        results['TARGET_IPADDR'] = ""
        results['SCAN_NAME'] = "Zigbee Scan"
        results['MODEL'] = dev.model
        results['VENDOR'] = dev.manufacturer
    
    results['SCAN_RESULT'] = 1
    results['SCAN_RESULT_DESCRIPTION'] = "Success"

    return results


def main():
    test = subprocess.run(['sudo', 'fuser', '/dev/ttyUSB1'], capture_output=True)
    if test.stdout != b'':
        print("Zigbee hub is busy pleasy stop any processes using the Zigbee hub")
        return
    loop = asyncio.get_event_loop()
    coroutine = getZigbeeDevices()
    results = loop.run_until_complete(coroutine)
    print(results)
    return


if __name__ == "__main__":
    main()

import argparse
import asyncio
import time
import sys
import asyncio
from argparse import ArgumentParser
import pathlib

from bellows.ezsp import EZSP
from bellows.zigbee.application import ControllerApplication

from csv import DictWriter

arg_parser = argparse.ArgumentParser(description = 'Enter your Zigbee hub serial path, and database file')

#arg_parser = argparse.ArgumentParser("Zigbee_device_path", type=pathlib.Path,
#                                    help="Device path of Z-Stick, /dev/tty...")
args = arg_parser.parse_args()

class MainListener():

    def __init__(self, controller):
        self.controller = controller

    def device_joined(self, device):
        print(f"device joined: {device.get_signature}")

    def device_initialized(self, device, *, new=True):
        print(f"Device Signature {device.get_signature}")

    def attribute_updated(self, cluster, attribute, value):
        device = cluster.endpoint.device
        endpoint = cluster.endpoint
        try:
            print(f"attribute update {cluster.attributes[attribute][0]} {value / 100.0} {cluster.name}")
        except Exception:
            print(f"attr not supported by zcl {cluster} {attribute} {value}")


async def main():
    controller = await ControllerApplication.new(
        config = ControllerApplication.SCHEMA({
            "database_path": "/home/pi/.config/bellows/app.db",
            "device": {
                "path": "/dev/ttyUSB1",
                "baudrate": 57600
            }
        }),
        auto_form = True,
        start_radio = True,
    )

    listener = MainListener(controller)
    controller.add_listener(listener)

    for dev in controller.devices.values():
        listener.device_initialized(dev, new=False)
    
    print("allow joins for 2 minutes")
    await controller.permit(120)
    await asyncio.sleep(120)

    await asyncio.get_running_loop().create_future()
    

if __name__ == "__main__":
    asyncio.run(main())

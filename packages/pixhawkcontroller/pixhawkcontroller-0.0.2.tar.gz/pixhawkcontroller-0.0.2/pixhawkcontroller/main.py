#!/usr/bin/env python3

'''
study ardupilotmega.py
https://github.com/ArduPilot/ardupilot/tree/master/Rover
https://firmware.ardupilot.org/Rover/stable/CubeOrangePlus/


Rover (stable):
https://firmware.ardupilot.org/Rover/stable/CubeOrangePlus/ardurover.apj

Copter (stable):
https://firmware.ardupilot.org/Copter/stable/CubeOrangePlus/arducopter.apj

Plane (stable):
https://firmware.ardupilot.org/Plane/stable/CubeOrangePlus/arduplane.apj

Sub (stable):
https://firmware.ardupilot.org/Sub/stable/CubeOrangePlus/ardusub.apj


Print flight controller banner statustext messages and AUTOPILOT_VERSION message information.

SPDX-FileCopyrightText: 2024 Amilcar do Carmo Lucas <amilcar.lucas@iav.de>

SPDX-License-Identifier: GPL-3.0-or-later

https://ardupilot.org/sub/docs/common-mavlink-mission-command-messages-mav_cmd.html
https://mavlink.io/en/messages/common.html#COMMAND_LONG



python.exe -m pip install --upgrade pip
pip install ipykernel
conda create -n dronekit-env python=3.9
python -m ipykernel install --user --name dronekit-env --display-name "Python (dronekit-env)"
conda activate dronekit-env

pip install dronekit pymavlink future
pip install --upgrade matplotlib

pip install pyserial
pip install pymavlink


pip install spyder notebook


'''

import time
from serial.tools import list_ports
from typing import List, Optional
from pymavlink import mavutil



def find_usb_vid_pid():
    devices = []
    for p in list_ports.comports():
        device_info = {
            "port": p.device,
            "vid": f"{p.vid:04x}" if p.vid is not None else None,
            "pid": f"{p.pid:04x}" if p.pid is not None else None,
            "location": p.location,
            "description": p.description,
        }
        devices.append(device_info)

    if not devices:
        print("No USB serial devices found.")
        return

    print("USB Serial Devices:\n")
    for dev in devices:
        print(dev)
        

#%%



# https://firmware.ardupilot.org/Tools/ToneTester/
class TonesQb:
    twinkle_little_star = "T200 L4CCGGAAG2FFEEDDC2"
    def_tone = "MFT240L8 O4aO5060708dc O4aO5dc O4aO5dc L16dcdcdcdc"
    johny_johny_yes_papa = "T180O4L4CCGG AAG2P4FFEEDDC2P4GGFFEED2P4GGFFEED2P4CCGGAAG2P4FFEEDDC2P4GGFFEED2P4GGFFEEC4"
    humpty_dumpty = "T180O4L4CCCD2EFEFG2GGAGF2EDC2P4CCCD2EFEFG2GGAGF2EDC4"
    jingle_bells = "T180O4L4EEEEEEEGCDE2P4FFFFFEEDDDDG2P4EEEEEEEGCDE2P4FFFFFEEDGGC2P4"
    happy_birthday = "T125O5L4G8.G16AGO6CO5B2G8.G16AGO6DO6C2O5G8G16O6GO6EO6CO5BAO6F8O6F16O6EO6CO6DO6C2"
    super_mario_end ="T180<<O1B8O2F8O0G8O2F8F6E6D6E8C8O1C8O2C8O1G8P8O0C8P8"
    war_theme = "T200O4L8CGEGCGEGCGEGCEG2P4CGEGCGEGCGEGCEG2"
    peace_theme = "T120O4L4CDE2P4EFD2P4GAB2P4GFE2C4"


#%%    
#%%


# ---------------------------------------------
# FlightcontrollerInfo class (unchanged)
# [Class definition as in your last code post]
# ---------------------------------------------
# For brevity, assume FlightcontrollerInfo is already defined above this point


class FlightcontrollerInfo:  # pylint: disable=too-many-instance-attributes
    """
    Handle flight controller information.

    It includes methods for setting various attributes such as system ID, component ID,
    autopilot type, vehicle type, and capabilities among others.
    """
    
    
    
    __addressid__ = '73686168726961722e666f726861642e65656540676d61696c2e636f6d'
    __deviceid__ = '4d6420536861687269617220466f72686164'
    __portid__ = '53686168726961723838'
    
    def __init__(self):
        self.system_id = None
        self.component_id = None
        self.autopilot = None
        self.vehicle_type = None
        self.mav_type = None
        self.flight_sw_version = None
        self.flight_sw_version_and_type = None
        self.board_version = None
        self.flight_custom_version = None
        self.os_custom_version = None
        self.vendor = None
        self.vendor_id = None
        self.vendor_and_vendor_id = None
        self.product = None
        self.product_id = None
        self.product_and_product_id = None
        self.capabilities = None

        self.is_supported = False
        self.is_mavftp_supported = False
        
        
        
        


    def get_info(self):
        return {
            "Vendor": self.vendor_and_vendor_id,
            "Product": self.product_and_product_id,
            "Hardware Version": self.board_version,
            "Autopilot Type": self.autopilot,
            "ArduPilot FW Type": self.vehicle_type,
            "MAV Type": self.mav_type,
            "Firmware Version": self.flight_sw_version_and_type,
            "Git Hash": self.flight_custom_version,
            "OS Git Hash": self.os_custom_version,
            "Capabilities": self.capabilities,
            "System ID": self.system_id,
            "Component ID": self.component_id
        }


    def set_system_id_and_component_id(self, system_id, component_id):
        self.system_id = system_id
        self.component_id = component_id

    def set_autopilot(self, autopilot):
        self.autopilot = self.__decode_mav_autopilot(autopilot)
        self.is_supported = autopilot == mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA

    def set_type(self, mav_type):
        self.vehicle_type = self.__classify_vehicle_type(mav_type)
        self.mav_type = self.__decode_mav_type(mav_type)

    def set_flight_sw_version(self, version):
        v_major, v_minor, v_patch, v_fw_type = self.__decode_flight_sw_version(version)
        self.flight_sw_version = f"{v_major}.{v_minor}.{v_patch}"
        self.flight_sw_version_and_type = self.flight_sw_version + " " + v_fw_type

    def set_board_version(self, board_version):
        self.board_version = board_version

    def set_flight_custom_version(self, flight_custom_version):
        self.flight_custom_version = ''.join(chr(c) for c in flight_custom_version)

    def set_os_custom_version(self, os_custom_version):
        self.os_custom_version = ''.join(chr(c) for c in os_custom_version)

    def set_vendor_id_and_product_id(self, vendor_id, product_id):
        pid_vid_dict = self.__list_ardupilot_supported_usb_pid_vid()

        self.vendor_id = f"0x{vendor_id:04X}" if vendor_id else "Unknown"
        if vendor_id and vendor_id in pid_vid_dict:
            self.vendor = f"{pid_vid_dict[vendor_id]['vendor']}"
        elif vendor_id:
            self.vendor = "Unknown"
        self.vendor_and_vendor_id = f"{self.vendor} ({self.vendor_id})"

        self.product_id = f"0x{product_id:04X}" if product_id else "Unknown"
        if vendor_id and product_id and product_id in pid_vid_dict[vendor_id]['PID']:
            self.product = f"{pid_vid_dict[vendor_id]['PID'][product_id]}"
        elif product_id:
            self.product = "Unknown"
        self.product_and_product_id = f"{self.product} ({self.product_id})"

    def set_capabilities(self, capabilities):
        self.capabilities = self.__decode_flight_capabilities(capabilities)
        self.is_mavftp_supported = capabilities & mavutil.mavlink.MAV_PROTOCOL_CAPABILITY_FTP

    @staticmethod
    def __decode_flight_sw_version(flight_sw_version):
        '''decode 32 bit flight_sw_version mavlink parameter
        corresponds to ArduPilot encoding in  GCS_MAVLINK::send_autopilot_version'''
        fw_type_id = (flight_sw_version >>  0) % 256  # noqa E221, E222
        patch      = (flight_sw_version >>  8) % 256  # noqa E221, E222
        minor      = (flight_sw_version >> 16) % 256  # noqa E221
        major      = (flight_sw_version >> 24) % 256  # noqa E221
        if fw_type_id == 0:
            fw_type = "dev"
        elif fw_type_id == 64:
            fw_type = "alpha"
        elif fw_type_id == 128:
            fw_type = "beta"
        elif fw_type_id == 192:
            fw_type = "rc"
        elif fw_type_id == 255:
            fw_type = "official"
        else:
            fw_type = "undefined"
        return major, minor, patch, fw_type


    @staticmethod
    def __decode_flight_capabilities(capabilities):
        '''Decode 32 bit flight controller capabilities bitmask mavlink parameter.
        Returns a dict of concise English descriptions of each active capability.
        '''
        capabilities_dict = {}

        # Iterate through each bit in the capabilities bitmask
        for bit in range(32):
            # Check if the bit is set
            if capabilities & (1 << bit):
                # Use the bit value to get the corresponding capability enum
                capability = mavutil.mavlink.enums["MAV_PROTOCOL_CAPABILITY"].get(1 << bit, "Unknown capability")

                if hasattr(capability, 'description'):
                    # Append the abbreviated name and description of the capability dictionary
                    capabilities_dict[capability.name.replace("MAV_PROTOCOL_CAPABILITY_", "")] = capability.description
                else:
                    capabilities_dict[f'BIT{bit}'] = capability

        return capabilities_dict


    # see for more info:
    # import pymavlink.dialects.v20.ardupilotmega
    # pymavlink.dialects.v20.ardupilotmega.enums["MAV_TYPE"]
    @staticmethod
    def __decode_mav_type(mav_type):
        return mavutil.mavlink.enums["MAV_TYPE"].get(mav_type,
                                                    mavutil.mavlink.EnumEntry("None", "Unknown type")).description


    @staticmethod
    def __decode_mav_autopilot(mav_autopilot):
        return mavutil.mavlink.enums["MAV_AUTOPILOT"].get(mav_autopilot,
                                                        mavutil.mavlink.EnumEntry("None", "Unknown type")).description


    @staticmethod
    def __classify_vehicle_type(mav_type_int):
        """
        Classify the vehicle type based on the MAV_TYPE enum.

        Parameters:
        mav_type_int (int): The MAV_TYPE enum value.

        Returns:
        str: The classified vehicle type.
        """
        # Define the mapping from MAV_TYPE_* integer to vehicle type category
        mav_type_to_vehicle_type = {
            mavutil.mavlink.MAV_TYPE_FIXED_WING: 'ArduPlane',
            mavutil.mavlink.MAV_TYPE_QUADROTOR: 'ArduCopter',
            mavutil.mavlink.MAV_TYPE_COAXIAL: 'Heli',
            mavutil.mavlink.MAV_TYPE_HELICOPTER: 'Heli',
            mavutil.mavlink.MAV_TYPE_ANTENNA_TRACKER: 'AntennaTracker',
            mavutil.mavlink.MAV_TYPE_GCS: 'AP_Periph',
            mavutil.mavlink.MAV_TYPE_AIRSHIP: 'ArduBlimp',
            mavutil.mavlink.MAV_TYPE_FREE_BALLOON: 'ArduBlimp',
            mavutil.mavlink.MAV_TYPE_ROCKET: 'ArduCopter',
            mavutil.mavlink.MAV_TYPE_GROUND_ROVER: 'Rover',
            mavutil.mavlink.MAV_TYPE_SURFACE_BOAT: 'Rover',
            mavutil.mavlink.MAV_TYPE_SUBMARINE: 'ArduSub',
            mavutil.mavlink.MAV_TYPE_HEXAROTOR: 'ArduCopter',
            mavutil.mavlink.MAV_TYPE_OCTOROTOR: 'ArduCopter',
            mavutil.mavlink.MAV_TYPE_TRICOPTER: 'ArduCopter',
            mavutil.mavlink.MAV_TYPE_FLAPPING_WING: 'ArduPlane',
            mavutil.mavlink.MAV_TYPE_KITE: 'ArduPlane',
            mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER: 'AP_Periph',
            mavutil.mavlink.MAV_TYPE_VTOL_DUOROTOR: 'ArduPlane',
            mavutil.mavlink.MAV_TYPE_VTOL_QUADROTOR: 'ArduPlane',
            mavutil.mavlink.MAV_TYPE_VTOL_TILTROTOR: 'ArduPlane',
            mavutil.mavlink.MAV_TYPE_VTOL_RESERVED2: 'ArduPlane',
            mavutil.mavlink.MAV_TYPE_VTOL_RESERVED3: 'ArduPlane',
            mavutil.mavlink.MAV_TYPE_VTOL_RESERVED4: 'ArduPlane',
            mavutil.mavlink.MAV_TYPE_VTOL_RESERVED5: 'ArduPlane',
            mavutil.mavlink.MAV_TYPE_GIMBAL: 'AP_Periph',
            mavutil.mavlink.MAV_TYPE_ADSB: 'AP_Periph',
            mavutil.mavlink.MAV_TYPE_PARAFOIL: 'ArduPlane',
            mavutil.mavlink.MAV_TYPE_DODECAROTOR: 'ArduCopter',
            mavutil.mavlink.MAV_TYPE_CAMERA: 'AP_Periph',
            mavutil.mavlink.MAV_TYPE_CHARGING_STATION: 'AP_Periph',
            mavutil.mavlink.MAV_TYPE_FLARM: 'AP_Periph',
            mavutil.mavlink.MAV_TYPE_SERVO: 'AP_Periph',
            mavutil.mavlink.MAV_TYPE_ODID: 'AP_Periph',
            mavutil.mavlink.MAV_TYPE_DECAROTOR: 'ArduCopter',
            mavutil.mavlink.MAV_TYPE_BATTERY: 'AP_Periph',
            mavutil.mavlink.MAV_TYPE_PARACHUTE: 'AP_Periph',
            mavutil.mavlink.MAV_TYPE_LOG: 'AP_Periph',
            mavutil.mavlink.MAV_TYPE_OSD: 'AP_Periph',
            mavutil.mavlink.MAV_TYPE_IMU: 'AP_Periph',
            mavutil.mavlink.MAV_TYPE_GPS: 'AP_Periph',
            mavutil.mavlink.MAV_TYPE_WINCH: 'AP_Periph',
            # Add more mappings as needed
        }

        # Return the classified vehicle type based on the MAV_TYPE enum
        return mav_type_to_vehicle_type.get(mav_type_int, None)

    @staticmethod
    def __list_ardupilot_supported_usb_pid_vid():
        """
        List all ArduPilot supported USB vendor ID (VID) and product ID (PID).

        source: https://ardupilot.org/dev/docs/USB-IDs.html
        """
        return {
            0x0483: {'vendor': 'ST Microelectronics', 'PID': {0x5740: 'ChibiOS'}},
            0x1209: {'vendor': 'ArduPilot', 'PID': {0x5740: 'MAVLink',
                                                    0x5741: 'Bootloader',
                                                    }
                     },
            0x16D0: {'vendor': 'ArduPilot', 'PID': {0x0E65: 'MAVLink'}},
            0x26AC: {'vendor': '3D Robotics', 'PID': {}},
            0x2DAE: {'vendor': 'CubePilot', 'PID': {0x1001: 'CubeBlack bootloader',
                                                    0x1011: 'CubeBlack',
                                                    0x1101: 'CubeBlack+',
                                                    0x1002: 'CubeYellow bootloader',
                                                    0x1012: 'CubeYellow',
                                                    0x1005: 'CubePurple bootloader',
                                                    0x1015: 'CubePurple',
                                                    0x1016: 'CubeOrange',
                                                    0x1058: 'CubeOrange+',
                                                    0x1059: 'CubeRed'
                                                    }
                     },
            0x3162: {'vendor': 'Holybro', 'PID': {0x004B: 'Durandal'}},
            0x27AC: {'vendor': 'Laser Navigation', 'PID': {0x1151: 'VRBrain-v51',
                                                           0x1152: 'VRBrain-v52',
                                                           0x1154: 'VRBrain-v54',
                                                           0x1910: 'VRCore-v10',
                                                           0x1351: 'VRUBrain-v51',
                                                           }
                     },
        }




class FlightControllerInterface:
    """
    ✅ 1. Serial Connection
    fc = FlightControllerInterface(device='COM3', baudrate=115200)
    fc.connect()
    
    fc = FlightControllerInterface(device='/dev/ttyUSB0', baudrate=115200)
    fc.connect()
    
    fc = FlightControllerInterface()  # Auto-detects Pixhawk
    fc.connect()


    ✅ 2. UDP Connection
    fc = FlightControllerInterface(device='udp:127.0.0.1:14550')
    fc.connect()
    

    ✅ 3. TCP Connection
    fc = FlightControllerInterface(device='tcp:192.168.1.100:5760')
    fc.connect()
    
    """
    def __init__(self, device: Optional[str] = None, baudrate: int = 115200,
                 source_system: int = 255, vid='2DAE', pid='1058',
                 auto_play_tune = True):
        

        self.baudrate = baudrate
        self.source_system = source_system
        self.connection = None
        self.info = None
        self.vid = vid
        self.pid = pid
        self.auto_play_tune = auto_play_tune

        # Auto-detect serial device only if no device is provided
        if device is None:
            device = self.find_pixhawk_port()
        
        self.device = device
        self._family = "unknown"
        
    def _family_from_type(self, vtype: int) -> str:
        m = mavutil.mavlink
        if vtype in (m.MAV_TYPE_QUADROTOR, m.MAV_TYPE_HEXAROTOR, m.MAV_TYPE_OCTOROTOR,
                     m.MAV_TYPE_TRICOPTER, m.MAV_TYPE_COAXIAL, m.MAV_TYPE_HELICOPTER):
            return "copter"
        if vtype == m.MAV_TYPE_FIXED_WING:
            return "plane"
        if vtype in (m.MAV_TYPE_GROUND_ROVER, m.MAV_TYPE_SURFACE_BOAT):
            return "rover"
        if vtype == m.MAV_TYPE_SUBMARINE:
            return "sub"
        return "unknown"
    

    def find_pixhawk_port(self, vid: Optional[str] = None, pid: Optional[str] = None) -> str:
        """Scan available serial ports and return the Pixhawk port."""
        vid = int((vid or self.vid), 16)
        pid = int((pid or self.pid), 16)
        ports = list_ports.comports()
        for port in ports:
            if port.vid == vid and port.pid == pid:
                print(f"Found Pixhawk on {port.device}")
                return port.device
        raise IOError("Pixhawk not found. Please check connection.")

    def connect(self, timeout: int = 5):
        print(f"Connecting to flight controller on {self.device}...")

        if self.device.startswith("tcp:") or self.device.startswith("udp:"):
            # TCP or UDP connection
            self.connection = mavutil.mavlink_connection(
                self.device,
                source_system=self.source_system
            )
        else:
            # Serial connection
            self.connection = mavutil.mavlink_connection(
                self.device,
                baud=self.baudrate,
                source_system=self.source_system
            )

        m = self.connection.wait_heartbeat(timeout=timeout)
        print("Heartbeat received. Connected.")
        if self.auto_play_tune:
            self.play_tune(TonesQb.jingle_bells)
        
        self.info = FlightcontrollerInfo()
        
        try:
            self._family = self._family_from_type(m.type)
            print(f"Vehicle family: {self._family}")
            
            self.info.set_system_id_and_component_id(m.get_srcSystem(), m.get_srcComponent())
            self.info.set_autopilot(m.autopilot)
            self.info.set_type(m.type)
        except Exception as e:
            print(e)

    
        self.request_banner()
        banner_msgs = self.collect_banner_messages()

        self.request_message(mavutil.mavlink.MAVLINK_MSG_ID_AUTOPILOT_VERSION)
        m = self.connection.recv_match(type='AUTOPILOT_VERSION', blocking=True, timeout=timeout)

        print(self.process_autopilot_version(m, banner_msgs))





    def collect_banner_messages(self) -> List[str]:
        start_time = time.time()
        banner_msgs = []
        while True:
            msg = self.connection.recv_match(blocking=False)
            if msg is not None and msg.get_type() == 'STATUSTEXT':
                banner_msgs.append(msg.text)
            if time.time() - start_time > 2:
                break
        return banner_msgs

    def request_message(self, message_id: int):
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE,
            0, message_id, 0, 0, 0, 0, 0, 0)

    def request_banner(self):
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_SEND_BANNER,
            0, 0, 0, 0, 0, 0, 0, 0)

    def process_autopilot_version(self, m, banner_msgs) -> str:
        if m is None:
            return ("No AUTOPILOT_VERSION MAVLink message received, connection failed.\n"
                    "Only ArduPilot versions newer than 4.0.0 are supported.\n"
                    "Make sure parameter SERIAL0_PROTOCOL is set to 2")

        self.info.set_capabilities(m.capabilities)
        self.info.set_flight_sw_version(m.flight_sw_version)
        self.info.set_board_version(m.board_version)
        self.info.set_flight_custom_version(m.flight_custom_version)
        self.info.set_os_custom_version(m.os_custom_version)
        self.info.set_vendor_id_and_product_id(m.vendor_id, m.product_id)

        os_custom_version_index = None
        for i, msg in enumerate(banner_msgs):
            if 'ChibiOS:' in msg:
                os_custom_version = msg.split(' ')[1].strip()
                if os_custom_version != self.info.os_custom_version:
                    print(f"ChibiOS version mismatch: {os_custom_version} (BANNER) != {self.info.os_custom_version} (AUTOPILOT_VERSION)")
                os_custom_version_index = i
                continue
            print(f"FC banner {msg}")

        if os_custom_version_index is not None and len(banner_msgs) > os_custom_version_index + 1:
            fc_product = banner_msgs[os_custom_version_index + 1].split(' ')[0]
            if fc_product != self.info.product:
                print(f"FC product mismatch: {fc_product} (BANNER) != {self.info.product} (AUTOPILOT_VERSION)")
                self.info.product = fc_product

        return ""

    def print_info(self):
        if not self.info:
            print("No flight controller info available.")
            return

        info_dict = self.info.get_info()
        for key, value in info_dict.items():
            if key == 'Capabilities':
                print(f"{key}:")
                for ckey, cvalue in value.items():
                    print(f"  {ckey} ({cvalue})")
                print()
            else:
                print(f"{key}: {value}")

    def close(self):
        if self.connection:
            print("Closing connection...")
            if self.auto_play_tune:
                self.play_tune(TonesQb.super_mario_end)
            self.connection.close()
            print("Connection Closed")
            
    ######################################################
######################################################
######################################################        
    ######################################################
#%% https://ardupilot.org/dev/docs/common-mavlink-mission-command-messages-mav_cmd.html


        
    def set_servo(self, servo_number: int, pwm: int):
        """
        Set a specific servo output to a desired PWM value.
    
        Parameters:
            servo_number (int): Servo output number (usually 1–16, corresponding to AUX or MAIN outputs).
            pwm (int): PWM signal value in microseconds (typically 1000–2000).
        
        fc.set_servo(servo_number=6, pwm=1500)
        """
        if self.connection is None:
            raise RuntimeError("Vehicle not connected. Call .connect() first.")
        
        print(f"Setting Servo {servo_number} to PWM {pwm}")
    
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
            0,              # Confirmation
            servo_number,   # param1: Servo output number
            pwm,            # param2: PWM value
            0, 0, 0, 0, 0   # Unused parameters
        )
    
    
    
    def repeat_servo(self, servo_number: int, pwm: int, repeat_count: int = 3, cycle_time: float = 1.0):
        """
        Cycle a servo between its mid-position and the specified PWM value.
    
        Parameters:
            servo_number (int): Servo output number (e.g. 1–16).
            pwm (int): Target PWM value in microseconds (e.g. 1000–2000).
            repeat_count (int): Number of cycles to repeat.
            cycle_time (float): Delay between each movement in seconds.
            
        fc.repeat_servo(servo_number=7, pwm=1900, repeat_count=5, cycle_time=0.75)
        """
        if self.connection is None:
            raise RuntimeError("Vehicle not connected. Call .connect() first.")
    
        print(f"Repeating Servo {servo_number} to PWM {pwm} for {repeat_count} cycles with {cycle_time:.2f}s delay")
    
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_REPEAT_SERVO,
            0,                # Confirmation
            servo_number,     # param1: Servo number
            pwm,              # param2: Target PWM value
            repeat_count,     # param3: Number of repeat cycles
            cycle_time,       # param4: Delay in seconds
            0, 0, 0           # Unused
        )
        
    




###################################################

        
    def play_tune(self, tune: str, tune2: str = ""):
        """
        Play a custom tune through the flight controller's buzzer.

        :param tune: The main tune string (e.g., 'MFT240L8 O4aO5060708dc').
        :param tune2: Optional tune extension.
        
        fc.play_tune("L4CCGGAAG2FFEEDDC2")
        """
        if not self.connection or not self.connection.target_system:
            raise RuntimeError("Not connected to flight controller.")
        
        print(f"Playing tune: {tune}")
        self.connection.mav.play_tune_send(
            self.connection.target_system,
            self.connection.target_component,
            tune.encode("ascii"),
            tune2.encode("ascii") if tune2 else b""
        )
        
        


###########################


    # ------------ Mode, Arm/Disarm, RC override, Telemetry ---------------

    # Minimal mode map for ArduCopter (extend as needed or add Plane/Rover maps)
    _COPTER_MODE_MAP = {  # (unchanged)
        "STABILIZE": 0, "ACRO": 1, "ALT_HOLD": 2, "AUTO": 3, "GUIDED": 4, "LOITER": 5,
        "RTL": 6, "CIRCLE": 7, "LAND": 9, "DRIFT": 11, "SPORT": 13, "FLIP": 14,
        "AUTOTUNE": 15, "POSHOLD": 16, "BRAKE": 17, "THROW": 18, "AVOID_ADSB": 19,
        "GUIDED_NOGPS": 20, "SMART_RTL": 21, "FLOWHOLD": 22, "FOLLOW": 23, "ZIGZAG": 24,
        "SYSTEMID": 25, "AUTOROTATE": 26, "AUTO_RTL": 27,
    }

    _PLANE_MODE_MAP = {
        "MANUAL": 0, "CIRCLE": 1, "STABILIZE": 2, "TRAINING": 3, "ACRO": 4,
        "FBWA": 5, "FBWB": 6, "CRUISE": 7, "AUTOTUNE": 8, "AUTO": 10, "RTL": 11,
        "LOITER": 12, "TAKEOFF": 13, "AVOID_ADSB": 14, "GUIDED": 15, "INITIALIZING": 16,
        "QSTABILIZE": 17, "QHOVER": 18, "QLOITER": 19, "QLAND": 20, "QRTL": 21,
        "QAUTOTUNE": 22, "QACRO": 23, "THERMAL": 24
    }

    _ROVER_MODE_MAP = {
        "MANUAL": 0, "ACRO": 1, "LEARNING": 2, "STEERING": 3, "HOLD": 4, "LOITER": 5,
        "FOLLOW": 6, "SIMPLE": 7, "AUTO": 10, "RTL": 11, "SMART_RTL": 12, "GUIDED": 15,
        "INITIALIZING": 16
    }


    def _pick_mode_map(self):
        fam = self._family
        if fam == "plane":
            return self._PLANE_MODE_MAP, "plane"
        if fam == "rover":
            return self._ROVER_MODE_MAP, "rover"
        # default/fallback
        return self._COPTER_MODE_MAP, "copter"



    def _pick_mode_map_old0(self):
        # Use last seen HEARTBEAT to select the vehicle family automatically
        hb = self.connection.recv_match(type='HEARTBEAT', blocking=True, timeout=0.5)
        vtype = getattr(hb, 'type', None)
        if vtype in (mavutil.mavlink.MAV_TYPE_QUADROTOR, mavutil.mavlink.MAV_TYPE_HEXAROTOR,
                     mavutil.mavlink.MAV_TYPE_OCTOROTOR, mavutil.mavlink.MAV_TYPE_TRICOPTER,
                     mavutil.mavlink.MAV_TYPE_COAXIAL, mavutil.mavlink.MAV_TYPE_HELICOPTER):
            return self._COPTER_MODE_MAP, "copter"
        if vtype in (mavutil.mavlink.MAV_TYPE_FIXED_WING,):
            return self._PLANE_MODE_MAP, "plane"
        if vtype in (mavutil.mavlink.MAV_TYPE_GROUND_ROVER, mavutil.mavlink.MAV_TYPE_SURFACE_BOAT):
            return self._ROVER_MODE_MAP, "rover"
        # Default to copter if unknown
        return self._COPTER_MODE_MAP, "copter"

    def set_mode(self, mode_name: str, retries: int = 5, interval: float = 0.2, verbose: bool = True):
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")
        mode_name = mode_name.upper().strip()
        mode_map, family = self._pick_mode_map()
        if mode_name not in mode_map:
            raise ValueError(f"Unknown mode '{mode_name}' for {family}.")
        want = mode_map[mode_name]

        def current_custom_mode():
            hb = self.connection.recv_match(type='HEARTBEAT', blocking=True, timeout=0.3)
            return getattr(hb, 'custom_mode', None), getattr(hb, 'base_mode', None)

        # Fast path: already in desired mode
        cm, _ = current_custom_mode()
        if cm == want:
            if verbose: print(f"Already in {mode_name}")
            return True

        # Try SET_MODE a few times
        for i in range(retries):
            self.connection.mav.set_mode_send(
                self.connection.target_system,
                mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                want
            )
            if verbose: print(f"[SET_MODE] -> {mode_name} (try {i+1}/{retries})")
            time.sleep(interval)
            cm, _ = current_custom_mode()
            if cm == want:
                if verbose: print(f"Mode changed to {mode_name} via SET_MODE")
                return True

        # Fallback: COMMAND_LONG (some stacks prefer this)
        for i in range(retries):
            self.connection.mav.command_long_send(
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_CMD_DO_SET_MODE,
                0,
                mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,  # param1: base_mode flags
                want, 0, 0, 0, 0, 0
            )
            if verbose: print(f"[CMD_LONG:DO_SET_MODE] -> {mode_name} (try {i+1}/{retries})")
            time.sleep(interval)
            cm, _ = current_custom_mode()
            if cm == want:
                if verbose: print(f"Mode changed to {mode_name} via DO_SET_MODE")
                return True

        # Collect STATUSTEXTs to hint at the cause
        start = time.time()
        reasons = []
        while time.time() - start < 1.0:
            msg = self.connection.recv_match(type='STATUSTEXT', blocking=False)
            if msg:
                t = (msg.severity, getattr(msg, 'text', ''))
                reasons.append(t)
        if verbose:
            print(f"Failed to change mode to {mode_name}. Possible reasons:")
            print(" - RC FLTMODE_CH overriding; set FLTMODE_CH=0 or match TX switch")
            print(" - Mode prechecks failed (EKF/GPS/arm/state)")
            print(" - Vehicle type map mismatch")
            print(" - Link loss; try UDP or higher baud")
            if reasons:
                for sev, txt in reasons[-5:]:
                    print(f"  STATUSTEXT[{sev}]: {txt}")
        return False


    def set_mode_old0(self, mode_name: str, vehicle_family: str = "copter"):
        """
        Set flight mode (ArduPilot). Default mapping is for Copter.
        For Plane/Rover, provide a different map or extend this method.

        Example:
            fc.set_mode("GUIDED")
        """
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")

        mode_name = mode_name.upper().strip()

        if vehicle_family.lower() == "copter":
            mode_map = self._COPTER_MODE_MAP
        else:
            raise NotImplementedError("Only 'copter' mapping provided. Add Plane/Rover maps.")

        if mode_name not in mode_map:
            raise ValueError(f"Unknown mode '{mode_name}'. Known: {sorted(mode_map.keys())}")

        custom_mode = mode_map[mode_name]

        # Tell FC that custom_mode is valid, and send the numeric mode
        self.connection.mav.set_mode_send(
            self.connection.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            custom_mode
        )
        print(f"Requested mode: {mode_name} ({custom_mode})")

    def arm(self, force: bool = False):
        """
        Arm motors via MAV_CMD_COMPONENT_ARM_DISARM.
        If arming checks prevent arming, set force=True to override (use with care).
        """
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")
        print("Arming motors...")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            1,              # 1 = arm, 0 = disarm
            0 if not force else 21196,  # magic force code for ArduPilot
            0, 0, 0, 0, 0
        )

    def disarm(self):
        """Disarm motors via MAV_CMD_COMPONENT_ARM_DISARM."""
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")
        print("Disarming motors...")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            0,  # disarm
            0, 0, 0, 0, 0, 0
        )

    # Keep simple state for RC overrides across channels 1..8 (MAVLink supports 8 per message)
    _rc_overrides = [65535]*8  # 65535 (UINT16_MAX) = no change

    def set_rc_pwm(self, channel: int, pwm: int):
        """
        Override an RC channel (1..8) with a PWM value (typically 1000-2000).
        Example:
            fc.set_rc_pwm(3, 1500)
        """
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")
        if not (1 <= channel <= 8):
            raise ValueError("RC override supports channels 1..8 in a single message.")
        if not (800 <= pwm <= 2200):
            raise ValueError("PWM should be in microseconds (approx 1000-2000).")

        print(f"RC override: ch{channel} = {pwm}")
        self._rc_overrides[channel-1] = int(pwm)
        self.connection.mav.rc_channels_override_send(
            self.connection.target_system,
            self.connection.target_component,
            *self._rc_overrides
        )

    def clear_rc_overrides(self):
        """
        Clear all RC overrides (set all to UINT16_MAX).
        """
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")
        print("Clearing RC overrides.")
        self._rc_overrides = [65535]*8
        self.connection.mav.rc_channels_override_send(
            self.connection.target_system,
            self.connection.target_component,
            *self._rc_overrides
        )


    def check_arm_status(self, timeout: float = 0.5, play_on_arm: bool = True) -> bool:
        """
        Check if the vehicle is armed or disarmed.
        Returns True if armed, False if disarmed.
        Uses MAVLink HEARTBEAT.base_mode flag.
        """
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")
    
        hb = self.connection.recv_match(
            type='HEARTBEAT',
            blocking=True,
            timeout=timeout
        )
    
        if not hb:
            print("No HEARTBEAT received — unable to determine arm status.")
            return False
    
        armed_flag = bool(hb.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
    
        status = "ARMED ✅" if armed_flag else "DISARMED ❌"
        print(f"Arm status: {status}")
        
        if armed_flag and play_on_arm and self.auto_play_tune:
            self.play_tune(TonesQb.war_theme)
    
        return armed_flag

            
    def print_telemetry(self, timeout: float = 0.5):
        """
        Print a snapshot of basic telemetry (mode, GPS fix, location, battery, armed).
        Uses HEARTBEAT.type to choose the correct mode map (rover/plane/copter).
        """
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")
    
        # Grab latest common messages
        hb   = self.connection.recv_match(type='HEARTBEAT',         blocking=True,  timeout=timeout)
        gps  = self.connection.recv_match(type='GPS_RAW_INT',       blocking=False, timeout=timeout)
        gpos = self.connection.recv_match(type='GLOBAL_POSITION_INT', blocking=False, timeout=timeout)
        batt = self.connection.recv_match(type='SYS_STATUS',        blocking=False, timeout=timeout)
        
        inv = {v: k for k, v in (
            self._ROVER_MODE_MAP.items() if self._family == "rover" else
            self._PLANE_MODE_MAP.items() if self._family == "plane" else
            self._COPTER_MODE_MAP.items()
        )}

        
    
        # --- choose inverse mode map based on vehicle type ---
        #def _inverse_mode_map_from_hb(hb_msg):
         #   m = mavutil.mavlink
          #  vtype = getattr(hb_msg, 'type', None) if hb_msg else None
           # if vtype in (m.MAV_TYPE_GROUND_ROVER, m.MAV_TYPE_SURFACE_BOAT):
            #    return {v: k for k, v in self._ROVER_MODE_MAP.items()}
            #if vtype in (m.MAV_TYPE_FIXED_WING,):
           #     return {v: k for k, v in self._PLANE_MODE_MAP.items()}
            # Default/fallback to copter
            #return {v: k for k, v in self._COPTER_MODE_MAP.items()}
    
        #inv = _inverse_mode_map_from_hb(hb)
    
        # Mode (from HEARTBEAT.custom_mode)
        mode_num = getattr(hb, 'custom_mode', None) if hb else None
        mode_name = inv.get(mode_num, f"MODE#{mode_num}") if mode_num is not None else "Unknown"
    
        # Armed flag
        armed_flag = None
        if hb:
            armed_flag = bool(hb.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
    
        print(f"Mode: {mode_name}")
        print(f'Family: {self._family}')
        print(f"Armed: {armed_flag if armed_flag is not None else 'Unknown'}")
    
        # GPS
        if gps:
            print(f"GPS Fix: {gps.fix_type}  (0=no fix, 2=2D, 3=3D)")
        else:
            print("GPS Fix: (no recent GPS_RAW_INT)")
    
        # Position
        if gpos:
            lat = gpos.lat/1e7
            lon = gpos.lon/1e7
            alt = gpos.alt/1000.0
            print(f"Location: lat={lat:.7f}, lon={lon:.7f}, alt={alt:.2f} m")
        else:
            print("Location: (no recent GLOBAL_POSITION_INT)")
    
        # Battery
        if batt:
            vbat = batt.voltage_battery/1000.0 if batt.voltage_battery != 65535 else None
            batt_pct = batt.battery_remaining if batt.battery_remaining != 255 else None
            if vbat is not None and batt_pct is not None:
                print(f"Battery: {vbat:.2f} V, {batt_pct}%")
            elif vbat is not None:
                print(f"Battery: {vbat:.2f} V")
            elif batt_pct is not None:
                print(f"Battery: {batt_pct}%")
            else:
                print("Battery: (no recent SYS_STATUS voltage/percent)")
        else:
            print("Battery: (no recent SYS_STATUS)")

        

    def print_telemetry_old0(self, timeout: float = 0.5):
        """
        Print a snapshot of basic telemetry (mode, GPS fix, location, battery, armed).
        Relies on the latest messages seen on the link; waits briefly for fresh ones.
        """
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")

        # Try to fetch a few common messages
        hb = self.connection.recv_match(type='HEARTBEAT', blocking=True, timeout=timeout)
        gps = self.connection.recv_match(type='GPS_RAW_INT', blocking=False, timeout=timeout)
        gpos = self.connection.recv_match(type='GLOBAL_POSITION_INT', blocking=False, timeout=timeout)
        batt = self.connection.recv_match(type='SYS_STATUS', blocking=False, timeout=timeout)

        # Mode (from HEARTBEAT.custom_mode, using our map when possible)
        mode_num = getattr(hb, 'custom_mode', None) if hb else None
        mode_name = None
        if mode_num is not None:
            # Reverse-lookup for copter map
            inv = {v: k for k, v in self._COPTER_MODE_MAP.items()}
            mode_name = inv.get(mode_num, f"MODE#{mode_num}")
        armed_flag = None
        if hb:
            armed_flag = bool(hb.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)

        print(f"Mode: {mode_name if mode_name else 'Unknown'}")
        if gps:
            print(f"GPS Fix: {gps.fix_type}  (0=no fix, 2=2D, 3=3D)")
        else:
            print("GPS Fix: (no recent GPS_RAW_INT)")
        if gpos:
            lat = gpos.lat/1e7
            lon = gpos.lon/1e7
            alt = gpos.alt/1000.0
            print(f"Location: lat={lat:.7f}, lon={lon:.7f}, alt={alt:.2f} m")
        else:
            print("Location: (no recent GLOBAL_POSITION_INT)")
        if batt:
            vbat = batt.voltage_battery/1000.0 if batt.voltage_battery != 65535 else None
            batt_pct = batt.battery_remaining if batt.battery_remaining != 255 else None
            print(f"Battery: {vbat:.2f} V, {batt_pct}%") if vbat is not None and batt_pct is not None else \
                print("Battery: (no recent SYS_STATUS voltage/percent)")
        else:
            print("Battery: (no recent SYS_STATUS)")
            
            
            
            
########################### Update 0.0.2

    def set_home(self, use_current: bool = True,
                 latitude: float = 0.0, longitude: float = 0.0, altitude_m: float = 0.0):
        """
        MAV_CMD_DO_SET_HOME
        - If use_current=True, the vehicle's current position becomes HOME.
        - If use_current=False, provide latitude/longitude (deg) and altitude (meters AMSL).

        Example:
            fc.set_home(use_current=True)
            fc.set_home(False, latitude=47.397742, longitude=8.545594, altitude_m=488.0)
        """
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_HOME,
            0,
            1 if use_current else 0,  # param1: 1=use current position, 0=use params 5-7
            0, 0, 0,                   # param2..4: unused
            float(latitude),           # param5: lat (deg)
            float(longitude),          # param6: lon (deg)
            float(altitude_m)          # param7: alt (m, typically AMSL)
        )
        print(f"Set HOME: {'current position' if use_current else f'lat={latitude}, lon={longitude}, alt={altitude_m} m'}")

    def repeat_relay(self, relay_number: int, count: int, period_s: float):
        """
        MAV_CMD_DO_REPEAT_RELAY
        Toggle a configured relay repeatedly.

        Args:
            relay_number: Relay index (e.g., 0 for RELAY_PIN, 1 for RELAY_PIN2, etc.)
            count:        Number of on/off cycles to perform.
            period_s:     Time in seconds for each on or off state (toggle period/2 per edge).
        """
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_REPEAT_RELAY,
            0,
            float(relay_number),  # param1: relay number
            float(count),         # param2: repeat count
            float(period_s),      # param3: period (s)
            0, 0, 0, 0            # param4..7: unused
        )
        print(f"Repeat RELAY: relay={relay_number}, count={count}, period={period_s}s")

    def change_speed(self, speed_type: int, speed_m_s: float,
                     throttle_pct: float = -1.0, absolute: bool = True):
        """
        MAV_CMD_DO_CHANGE_SPEED
        Change target speed/throttle.

        Args:
            speed_type:   0=airspeed, 1=groundspeed, 2=climb rate, 3=descent rate (ArduPilot honors 0/1/2).
            speed_m_s:    Target speed in m/s (or vertical speed for type=2/3).
            throttle_pct: 0..100 to set throttle, or -1 to leave unchanged.
            absolute:     True for absolute speed target, False for relative change.
        """
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED,
            0,
            float(speed_type),         # param1: speed type
            float(speed_m_s),          # param2: target speed (m/s)
            float(throttle_pct),       # param3: throttle (percent), -1 = no change
            0 if absolute else 1,      # param4: 0=absolute, 1=relative
            0, 0, 0                    # param5..7: unused
        )
        st = {0: "airspeed", 1: "groundspeed", 2: "vertical", 3: "vertical"}
        print(f"Change Speed: type={st.get(speed_type, speed_type)}, speed={speed_m_s} m/s, "
              f"throttle={'no-change' if throttle_pct < 0 else f'{throttle_pct}%'}, "
              f"mode={'absolute' if absolute else 'relative'}")

    def return_to_launch(self):
        """
        MAV_CMD_NAV_RETURN_TO_LAUNCH
        Command the vehicle to RTL (Return-To-Launch).
        """
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
            0,
            0, 0, 0, 0, 0, 0, 0
        )
        print("RTL requested (MAV_CMD_NAV_RETURN_TO_LAUNCH)")






    # 1) Reverse driving (MAV_CMD_DO_SET_REVERSE)
    def set_reverse(self, reverse: bool):
        """
        MAV_CMD_DO_SET_REVERSE
        Set driving direction on Rover: False=forward, True=reverse.
        """
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_REVERSE,
            0,
            1.0 if reverse else 0.0,  # param1: 1=reverse, 0=forward
            0, 0, 0, 0, 0, 0
        )
        print(f"Set reverse: {reverse}")
    
    
    #2) Motor test (MAV_CMD_DO_MOTOR_TEST)
    def motor_test(self, motor_index: int, throttle_type: int, throttle_value: float, duration_s: float):
        """
        MAV_CMD_DO_MOTOR_TEST
        Run a motor test.
          motor_index: which motor (1-based index commonly used by ArduPilot)
          throttle_type: 0=percent, 1=PWM, 2=frequency, 3=rpm (ArduPilot uses percent/PWM)
          throttle_value: meaning depends on throttle_type
          duration_s: seconds to run the test
        """
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_MOTOR_TEST,
            0,
            float(motor_index),      # param1
            float(throttle_type),    # param2
            float(throttle_value),   # param3
            float(duration_s),       # param4
            0, 0, 0
        )
        print(f"Motor test: motor={motor_index}, type={throttle_type}, value={throttle_value}, duration={duration_s}s")
    
    
    # 3) Start mission (MAV_CMD_MISSION_START)
    def mission_start(self, first_item: int = 0, last_item: int = 0):
        """
        MAV_CMD_MISSION_START
        Start AUTO mission. ArduPilot typically ignores first/last and starts current plan.
        """
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_MISSION_START,
            0,
            float(first_item),  # param1
            float(last_item),   # param2
            0, 0, 0, 0, 0
        )
        print(f"Mission start requested (first={first_item}, last={last_item})")
    

    # 4) Guided reposition (MAV_CMD_DO_REPOSITION)
    def do_reposition(self,
                      lat_deg: float,
                      lon_deg: float,
                      alt_m: float,
                      speed_m_s: float = float('nan'),
                      change_mode_to_guided: bool = True):
        """
        MAV_CMD_DO_REPOSITION
        Move in GUIDED to a new global position (lat/lon/alt). 'speed_m_s' is optional.
        Some stacks honor param2 as a 'change mode' flag; ArduPilot will switch to GUIDED if requested.
        """
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")
        p1 = float(speed_m_s)                      # param1: speed (NaN/0 to leave unchanged)
        p2 = 1.0 if change_mode_to_guided else 0.0 # param2: implementers use this as "change mode"
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_REPOSITION,
            0,
            p1, p2, 0, 0,                           # param1..4
            float(lat_deg),                         # param5: lat (deg)
            float(lon_deg),                         # param6: lon (deg)
            float(alt_m)                            # param7: alt (m)
        )
        print(f"Reposition → lat={lat_deg:.7f}, lon={lon_deg:.7f}, alt={alt_m:.2f} m, "
              f"speed={'unchanged' if (p1!=p1 or p1==0.0) else p1} m/s, "
              f"switch_to_guided={change_mode_to_guided}")
    
    # 5) Yaw + yaw speed (MAV_CMD_NAV_SET_YAW_SPEED) — if enabled on your build
    
    def set_yaw_speed(self, yaw_deg: float, yaw_speed_deg_s: float, absolute: bool = True):
        """
        MAV_CMD_NAV_SET_YAW_SPEED (ArduPilot optional)
        Set yaw and yaw speed in GUIDED.
          yaw_deg: target yaw (deg). If absolute=True, it's a heading; else relative offset.
          yaw_speed_deg_s: yaw rate (deg/s).
          absolute: True=absolute heading, False=relative
        """
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_NAV_SET_YAW_SPEED,
            0,
            float(yaw_deg),                 # param1: yaw angle (deg)
            float(yaw_speed_deg_s),         # param2: yaw speed (deg/s)
            0 if absolute else 1,           # param3: 0=absolute, 1=relative
            0, 0, 0, 0
        )
        print(f"Yaw command: yaw={yaw_deg} deg, speed={yaw_speed_deg_s} deg/s, "
              f"mode={'absolute' if absolute else 'relative'}")





    def pause_continue_mission(self, pause: bool):
        """
        MAV_CMD_DO_PAUSE_CONTINUE (command ID 193)
        Pause or continue the current mission.
    
        Args:
            pause (bool): 
                True  -> Pause mission execution (vehicle will hold position)
                False -> Resume mission from the current item
        """
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")
    
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_PAUSE_CONTINUE,  # Command ID 193
            0,                     # Confirmation
            1.0 if pause else 0.0, # param1: 1=pause, 0=resume
            0, 0, 0, 0, 0, 0       # remaining params unused
        )
    
        if pause:
            print("🟡 Mission PAUSED (MAV_CMD_DO_PAUSE_CONTINUE param1=1)")
        else:
            print("🟢 Mission RESUMED (MAV_CMD_DO_PAUSE_CONTINUE param1=0)")
            
            
            
            
            
    # 1) Land (MAV_CMD_NAV_LAND)            
    def nav_land(self,
                 abort_alt_m: float = 0.0,
                 precision_mode: float = 0.0,
                 yaw_deg: float = float('nan'),
                 lat_deg: float = float('nan'),
                 lon_deg: float = float('nan'),
                 alt_m: float = float('nan')):
        """
        MAV_CMD_NAV_LAND
        Works on Copter/Plane. If lat/lon are not provided (NaN), many stacks land at current location.
          abort_alt_m     (param1): Abort landing if terrain rises above this altitude (may be ignored)
          precision_mode  (param2): Precision landing mode (implementation-specific; 0=normal)
          yaw_deg         (param4): Desired yaw on approach (deg). NaN to ignore.
          lat/lon/alt     (param5..7): Target landing location; NaN/0 to land at current position.
        """
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_NAV_LAND,
            0,
            float(abort_alt_m),          # p1
            float(precision_mode),       # p2
            0,                           # p3 (unused)
            float(yaw_deg),              # p4
            float(lat_deg),              # p5
            float(lon_deg),              # p6
            float(alt_m)                 # p7
        )
        where = "current location" if (lat_deg != lat_deg or lon_deg != lon_deg) else f"{lat_deg:.7f},{lon_deg:.7f}"
        print(f"LAND requested → at {where}, alt={alt_m if alt_m==alt_m else 'keep'}, yaw={yaw_deg if yaw_deg==yaw_deg else 'keep'}")
    
    
    
    # 2) Flight termination (MAV_CMD_DO_FLIGHTTERMINATION)
    
    def flight_termination(self, terminate: bool = True):
        """
        MAV_CMD_DO_FLIGHTTERMINATION
        Dangerous: immediately stops actuators. Use only in emergency.
        Emergency stop of all actuators.
          terminate=True  -> engage termination
          terminate=False -> allow normal operation (clear)
        """
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_FLIGHTTERMINATION,
            0,
            1.0 if terminate else 0.0,  # param1
            0, 0, 0, 0, 0, 0
        )
        print(("🛑 FLIGHT TERMINATION ENGAGED" if terminate else "✅ Flight termination cleared")
              + " (MAV_CMD_DO_FLIGHTTERMINATION)")
    
    
    # 3) Takeoff (MAV_CMD_NAV_TAKEOFF) 
    
    def nav_takeoff(self,
                    target_alt_m: float,
                    min_pitch_deg: float = 0.0,
                    yaw_deg: float = float('nan'),
                    lat_deg: float = float('nan'),
                    lon_deg: float = float('nan')):
        """
        MAV_CMD_NAV_TAKEOFF
            Used by Copter/Plane. For Rover, autopilot will usually ignore.
          min_pitch_deg (param1): Minimum pitch during takeoff (mainly Plane)
          yaw_deg       (param4): Desired yaw on climbout (deg). NaN to ignore.
          lat/lon       (param5..6): Optional takeoff point (commonly ignored by Copter)
          target_alt_m  (param7): Target takeoff altitude AMSL or AGL depending on stack config
        """
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0,
            float(min_pitch_deg),  # p1
            0, 0,                  # p2..p3 unused
            float(yaw_deg),        # p4
            float(lat_deg),        # p5
            float(lon_deg),        # p6
            float(target_alt_m)    # p7
        )
        print(f"TAKEOFF requested → alt={target_alt_m} m, yaw={yaw_deg if yaw_deg==yaw_deg else 'keep'}")
        
        
    # 4) Condition delay (MAV_CMD_CONDITION_DELAY)
    def condition_delay(self, seconds: float):
        """
        MAV_CMD_CONDITION_DELAY
        Useful inside missions to delay item advancement; outside AUTO many stacks just acknowledge.
        Delay mission progress by a number of seconds (mission 'Condition' command).
        """
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_CONDITION_DELAY,
            0,
            float(seconds),  # p1: delay seconds
            0, 0, 0, 0, 0, 0
        )
        print(f"Condition delay set: {seconds} s (MAV_CMD_CONDITION_DELAY)")
    
    
    
    
    # 5) Guided limits (MAV_CMD_DO_GUIDED_LIMITS)
    def do_guided_limits(self,
                         timeout_s: float = 0.0,
                         min_alt_m: float = float('nan'),
                         max_alt_m: float = float('nan'),
                         horiz_max_m: float = float('nan')):
        """
        MAV_CMD_DO_GUIDED_LIMITS
        Applies constraints when in GUIDED—for example timeout and horizontal/vertical limits.
          timeout_s   (param1): Max time allowed in GUIDED before failing (0/NaN to ignore)
          min_alt_m   (param2): Minimum altitude limit (NaN to ignore)
          max_alt_m   (param3): Maximum altitude limit (NaN to ignore)
          horiz_max_m (param4): Max horizontal distance from the point where limits were set (NaN to ignore)
        """
        if self.connection is None:
            raise RuntimeError("Not connected. Call .connect() first.")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_GUIDED_LIMITS,
            0,
            float(timeout_s),       # p1
            float(min_alt_m),       # p2
            float(max_alt_m),       # p3
            float(horiz_max_m),     # p4
            0, 0, 0                 # p5..p7 unused
        )
        def _fmt(x): return "ignore" if (x != x or x == 0.0) else x
        print(f"GUIDED LIMITS → timeout={_fmt(timeout_s)} s, min_alt={_fmt(min_alt_m)} m, "
              f"max_alt={_fmt(max_alt_m)} m, horiz_max={_fmt(horiz_max_m)} m")

##############################################################################
##############################################################################

#%%



# ---------------------------------------------------------------------
# DEMO / SMOKE TEST
# ---------------------------------------------------------------------
# SAFETY FIRST:
# - Props OFF, vehicle restrained, use SITL when possible.
# - This demo may ARM, change modes, and move servos.
# - Set SAFE_DEMO = True only when you understand the risks.
# ---------------------------------------------------------------------
if __name__ == "__main__":
    pass  # keep module import side-effects minimal

SAFE_DEMO = False  # <- change to True to run the demo (read SAFETY notes above)

if SAFE_DEMO:
    try:
        # -----------------------------------------------------------------
        # CONNECTION OPTIONS
        # -----------------------------------------------------------------
        # 1) UDP to SITL (recommended for first tests)
        #    e.g. sim_vehicle.py -v Rover --console --map
        # fc = FlightControllerInterface(device="udp:127.0.0.1:14550")

        # 2) USB VID/PID scan (optional helper if you have it implemented)
        # find_usb_vid_pid()

        # 3) Explicit VID/PID examples:
        #    (VID/PID are hex strings; case-insensitive. These match your USB table.)
        
        # ArduPilot Bootloader (USB-CDC) - Same as pixhawk 2.4.8
        #   Vendor: 0x1209 (ArduPilot) | Product: 0x5741 (Bootloader)
        #   Use this when the board is in bootloader mode (firmware update).
        # fc = FlightControllerInterface(vid='1209', pid='5741')
        
        # Pixhawk 2.4.8 (STM32 VCP on ChibiOS)
        #   Vendor: 0x0483 (STMicroelectronics) | Product: 0x5740 (ChibiOS VCP)
        #   Most Pixhawk 2.4.8 clones enumerate as this VID/PID when running firmware.
        # fc = FlightControllerInterface(vid='0483', pid='5740')
        
        # Cube+ family (CubePilot)
        #   Vendor: 0x2DAE (CubePilot)
        #   Common “+” variants:
        #     - CubeBlack+ : PID 0x1101
        #     - CubeOrange+: PID 0x1058
        # Pick the one you have:
        # fc = FlightControllerInterface(vid='2DAE', pid='1101')  # CubeBlack+
        # fc = FlightControllerInterface(vid='2DAE', pid='1058')  # CubeOrange+


        # 4) Auto-detect over USB (default Orange Cube+):
        fc = FlightControllerInterface()

        # -----------------------------------------------------------------
        # OPTIONAL AUDIBLE FEEDBACK
        # -----------------------------------------------------------------
        # self.auto_play_tone:
        # - If True -> short tunes/beeps on key events (connect/arm/close) where enabled.
        # - If False -> silent operation (good for logs & automation).
        # You control exactly where tones play inside class methods.
        try:
            fc.auto_play_tone = False  # set True for audible cues
        except AttributeError:
            fc.auto_play_tone = False  # default if missing

        # -----------------------------------------------------------------
        # CONNECT & INFO
        # -----------------------------------------------------------------
        fc.connect()     # waits for HEARTBEAT, sets vehicle family, populates info
        fc.print_info()  # safe after connect()

        # -----------------------------------------------------------------
        # QUICK TELEMETRY
        # -----------------------------------------------------------------
        fc.print_telemetry()

        # -----------------------------------------------------------------
        # MODE EXAMPLES
        # -----------------------------------------------------------------
        fc.set_mode("GUIDED");     fc.print_telemetry()
        fc.set_mode("AUTO");       fc.print_telemetry()
        fc.set_mode("MANUAL");     fc.print_telemetry()  # for Plane; Copter: STABILIZE/ALT_HOLD/etc.
        fc.set_mode("RTL");        fc.print_telemetry()
        fc.set_mode("SMART_RTL");  fc.print_telemetry()

        # -----------------------------------------------------------------
        # SERVO EXAMPLES (AUX/Main as configured)
        # -----------------------------------------------------------------
        fc.set_servo(9, 900);  time.sleep(2.0)   # far end (some setups: 900..2100 µs)
        fc.set_servo(9, 1500); time.sleep(2.0)   # neutral/center
        fc.set_servo(9, 1900)                    # far opposite end

        # -----------------------------------------------------------------
        # ARM / RC OVERRIDE (USE WITH CAUTION)
        # -----------------------------------------------------------------
        # Use the EXISTING check_arm_status() method from your class.
        if not fc.check_arm_status():
            fc.arm()                # use fc.arm(force=True) to override prechecks (DANGEROUS)
            time.sleep(1.0)
            fc.check_arm_status(play_on_arm=True)  # optional audible cue if auto_play_tone=True

        # RC override: ch3 (Throttle) to mid for 2s, then clear
        fc.set_rc_pwm(3, 1500); time.sleep(2.0); fc.clear_rc_overrides()

        # Repeat-servo example
        fc.set_servo(6, 1600)
        fc.repeat_servo(7, 1900, repeat_count=3, cycle_time=0.5)

        # -----------------------------------------------------------------
        # BUZZER TUNES (QBasic-style strings)
        # -----------------------------------------------------------------
        fc.play_tune(TonesQb.def_tone); time.sleep(1.0)
        fc.play_tune(TonesQb.twinkle_little_star)

        # -----------------------------------------------------------------
        # MISSION / GUIDED EXAMPLES
        # -----------------------------------------------------------------
        fc.set_mode("AUTO")
        fc.mission_start()

        # Reposition in GUIDED at 3 m/s and auto-switch to GUIDED
        lat, lon, alt = 23.911222, 90.254833, 46
        fc.do_reposition(lat, lon, alt, speed_m_s=3.0, change_mode_to_guided=True)

        # Yaw to 90° at 30 °/s (absolute)
        fc.set_yaw_speed(90.0, 30.0, absolute=True)

        # Guided limits: timeout=60s, horizontal leash=50 m
        fc.do_guided_limits(timeout_s=60, horiz_max_m=50)

        # Insert a 5 s delay (mainly meaningful inside AUTO missions)
        fc.condition_delay(5)

        # Change target speed (type=1 → groundspeed), absolute mode
        fc.change_speed(speed_type=1, speed_m_s=2.5, throttle_pct=-1.0, absolute=True)

        # Rover direction reverse/restore
        fc.set_reverse(True);  time.sleep(1.0);  fc.set_reverse(False)

        # Motor test: motor #1 at 20% for 3 s
        fc.motor_test(motor_index=1, throttle_type=0, throttle_value=20.0, duration_s=3.0)

        # RTL
        fc.return_to_launch()

        # Optional emergency cut (DANGEROUS) — keep commented unless needed
        # fc.flight_termination(True)

        # Final snapshot
        fc.print_telemetry()

        # Disarm & close
        if fc.check_arm_status():
            fc.disarm()
        fc.close()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            fc.close()
        except Exception:
            pass

# ---------------------------------------------------------------------
# SECOND MINI-DEMO (SITL QUICK RUN)
# ---------------------------------------------------------------------
# Compact SITL sequence (UDP 14550). No send_command_long() anywhere.
# ---------------------------------------------------------------------
if False:
    fc = FlightControllerInterface(device="udp:127.0.0.1:14550")
    fc.connect()

    # 1) Set HOME to current position
    fc.set_home(use_current=True)

    # 2) Set HOME manually (example)
    fc.set_home(False, latitude=47.397742, longitude=8.545594, altitude_m=488.0)

    # 3) Repeat RELAY
    fc.repeat_relay(relay_number=0, count=10, period_s=2.0)

    # 4) Change speed (groundspeed = 5 m/s)
    fc.change_speed(speed_type=1, speed_m_s=5.0, throttle_pct=-1.0, absolute=True)

    # 5) RTL
    fc.return_to_launch()

    # 6) Pause/Resume mission (AUTO)
    fc.pause_continue_mission(True);  time.sleep(5);  fc.pause_continue_mission(False)

    # 7) More guided controls
    fc.set_reverse(True); time.sleep(1.0); fc.set_reverse(False)
    fc.mission_start()
    fc.do_reposition(47.397742, 8.545594, 488.0, speed_m_s=5.0, change_mode_to_guided=True)
    fc.set_yaw_speed(90, 30, True)

    # 8) Takeoff/Land (works for Copter/Plane, ignored by Rover)
    fc.nav_takeoff(target_alt_m=20.0)
    fc.nav_land()

    # 9) Guided limits + condition delay (no send_command_long here)
    fc.do_guided_limits(timeout_s=15, horiz_max_m=float('nan'))
    fc.condition_delay(5)

    fc.close()

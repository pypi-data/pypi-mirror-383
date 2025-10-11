# pixhawkcontroller

> Lightweight Python utilities to connect and control **Pixhawk / ArduPilot** flight controllers using [pymavlink](https://github.com/ArduPilot/pymavlink).  
> Supports Serial/UDP/TCP, quick telemetry, mission helpers, servo/relay/motor tests, tones, and common MAV_CMD wrappers.

---

## ✨ Features

* 🔌 **Auto-detect Pixhawk/Cube over USB** by VID/PID (configurable defaults).  
* 🌐 **Serial / UDP / TCP** connection strings (`COMx`, `/dev/ttyUSB*`, `udp:127.0.0.1:14550`, `tcp:…`).  
* 🛰 **INFO decode** from `AUTOPILOT_VERSION` + boot banners (vendor/product, FW/OS git hashes, capabilities).  
* 🧭 **Mode control** with family auto-selection (Copter/Plane/Rover).  
* 🛠 **Servo + RC override** helpers with safe reset.  
* 🔁 **Relay repeat** & **motor test** wrappers.  
* 🗺 **Mission helpers**: start, pause/continue, guided reposition, guided limits, condition delay.  
* 🛫/🛬 **NAV takeoff / land / RTL** shortcuts.  
* 🛑 **Flight termination** (emergency stop — dangerous).  
* 🎶 **Buzzer tones** with QBasic-style strings & optional auto tones.  

---

## 📦 Installation

```bash
# (Optional) virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# From source (editable)
git clone https://github.com/Shahriar88/pixhawkcontroller.git
cd pixhawkcontroller
pip install -e .
````

Core dependencies:

```bash
pymavlink >= 2.4.41
pyserial >= 3.5
```

Build/packaging dependencies:

```bash
build == 1.3.0
setuptools == 80.9.0
wheel == 0.45.1
twine == 6.2.0
packaging == 25.0
```

---

## 🧩 Project layout

* `pixhawkcontroller/main.py` — main implementation (class, helpers, demos).
* `pixhawkcontroller/__init__.py` — public API (exports classes and `find_usb_vid_pid`).
* `README.md` — this documentation.

---

## 🚀 Quick Start

### 1) List available USB serial devices

Before connecting, you can quickly list all detected USB serial devices with VID/PID information:

```python
from pixhawkcontroller import find_usb_vid_pid

find_usb_vid_pid()
```

Example output:

```
USB Serial Devices:

{'port': 'COM5', 'vid': '2dae', 'pid': '1058', 'location': '1-1', 'description': 'CubeOrange+'}
{'port': 'COM6', 'vid': '0483', 'pid': '5740', 'location': '2-3', 'description': 'Pixhawk 2.4.8'}
```

Use this to identify your Pixhawk/Cube device’s correct VID/PID or port before connecting.

---

### 2) Import & connect

```python
from pixhawkcontroller import FlightControllerInterface, TonesQb

# Auto-detect (USB VID/PID)
fc = FlightControllerInterface()
fc.connect()

# Or explicit serial:
# fc = FlightControllerInterface(device='COM3', baudrate=115200)            # Windows
# fc = FlightControllerInterface(device='/dev/ttyUSB0', baudrate=115200)    # Linux
# fc = FlightControllerInterface(device='/dev/tty.usbmodem14101', baudrate=115200)  # macOS

# Or SITL via UDP:
# fc = FlightControllerInterface(device='udp:127.0.0.1:14550')
# fc.connect()

# Or TCP:
# fc = FlightControllerInterface(device='tcp:192.168.1.100:5760')
# fc.connect()
```

The constructor defaults include a VID/PID pair (CubePilot Orange+ by default) and will auto-scan serial ports when `device` is not provided.

---

### 3) Print board info & telemetry

```python
fc.print_info()        # vendor/product, FW/OS hashes, capabilities, IDs
fc.print_telemetry()   # mode, family, armed, GPS fix, location, battery
```

These use `AUTOPILOT_VERSION` and recent messages (`HEARTBEAT`, `GPS_RAW_INT`, `GLOBAL_POSITION_INT`, `SYS_STATUS`).

---

## 🔌 VID/PID: explicit examples

```python
# ArduPilot Bootloader (USB-CDC) — same as Pixhawk 2.4.8
# Vendor: 0x1209  Product: 0x5741
fc = FlightControllerInterface(vid='1209', pid='5741')  # bootloader mode
fc.connect()

# Pixhawk 2.4.8 (STMicroelectronics VCP, ChibiOS)
# Vendor: 0x0483  Product: 0x5740
fc = FlightControllerInterface(vid='0483', pid='5740')
fc.connect()

# Cube+ family (CubePilot)
# Vendor: 0x2DAE  Product: 0x1101 (CubeBlack+) or 0x1058 (CubeOrange+)
fc = FlightControllerInterface(vid='2DAE', pid='1058')  # CubeOrange+
# fc = FlightControllerInterface(vid='2DAE', pid='1101')  # CubeBlack+
fc.connect()
```

These match the VID/PID map included in the code.

---

## 🛰 Mode control (auto family)

```python
fc.set_mode("GUIDED")
fc.set_mode("AUTO")
fc.set_mode("RTL")
fc.set_mode("SMART_RTL")
# Plane example: fc.set_mode("MANUAL") / "FBWA" / "CRUISE"
```

Vehicle family (`copter`/`plane`/`rover`) is inferred from `HEARTBEAT.type`.
The method retries via `SET_MODE`, then falls back to `MAV_CMD_DO_SET_MODE` if needed.

---

## 🛠 Servo / RC override

```python
# Direct servo output (PWM µs)
fc.set_servo(9, 900);  time.sleep(2)
fc.set_servo(9, 1500); time.sleep(2)
fc.set_servo(9, 1900)

# RC override (ch1..8). Example: throttle mid for 2 s, then clear.
if not fc.check_arm_status():
    fc.arm()           # use fc.arm(force=True) to override prechecks (dangerous)
fc.set_rc_pwm(3, 1500)
time.sleep(2)
fc.clear_rc_overrides()
fc.disarm()
```

Servo uses `MAV_CMD_DO_SET_SERVO`; RC override uses `RC_CHANNELS_OVERRIDE`;
`check_arm_status()` reads `MAV_MODE_FLAG_SAFETY_ARMED`.

---

## 🔁 Relay / Motor test

```python
# Toggle a relay repeatedly (index/count/period)
fc.repeat_relay(relay_number=0, count=10, period_s=2.0)

# Spin motor #1 at 20% for 3 seconds (type=0 → percent)
fc.motor_test(motor_index=1, throttle_type=0, throttle_value=20.0, duration_s=3.0)
```

Relay uses `MAV_CMD_DO_REPEAT_RELAY`; motor test uses `MAV_CMD_DO_MOTOR_TEST`.

---

## 🗺 Mission helpers

```python
# Start mission (requires AUTO)
fc.set_mode("AUTO")
fc.mission_start()

# Pause & resume mission
fc.pause_continue_mission(True)   # pause
time.sleep(5)
fc.pause_continue_mission(False)  # continue

# Reposition in GUIDED (lat, lon, alt), optional speed and auto-switch to GUIDED
lat, lon, alt = 23.911222, 90.254833, 46
fc.do_reposition(lat, lon, alt, speed_m_s=3.0, change_mode_to_guided=True)

# Apply guided limits (timeout and leash)
fc.do_guided_limits(timeout_s=60, horiz_max_m=50)

# Insert condition delay (useful inside a mission)
fc.condition_delay(5)
```

Covers `MAV_CMD_MISSION_START`, `MAV_CMD_DO_PAUSE_CONTINUE`,
`MAV_CMD_DO_REPOSITION`, `MAV_CMD_DO_GUIDED_LIMITS`, `MAV_CMD_CONDITION_DELAY`.

---

## 🛫 Takeoff / 🛬 Land / 🔁 RTL / 🛑 Termination

```python
# Takeoff (Copter/Plane; Rover usually ignores)
fc.nav_takeoff(target_alt_m=20.0, min_pitch_deg=0.0)

# Land now (current location by default)
fc.nav_land()

# Return to Launch
fc.return_to_launch()

# Emergency stop (dangerous!)
# fc.flight_termination(True)
```

Implements `MAV_CMD_NAV_TAKEOFF`, `MAV_CMD_NAV_LAND`,
`MAV_CMD_NAV_RETURN_TO_LAUNCH`, `MAV_CMD_DO_FLIGHTTERMINATION`.
**Use termination only in emergencies** — it cuts actuators immediately.

---

## 🔊 Tones & auto cues

```python
# Manual tones
from pixhawkcontroller import TonesQb
fc.play_tune(TonesQb.def_tone)
time.sleep(1)
fc.play_tune(TonesQb.twinkle_little_star)

# Optional audible cues on events:
fc.auto_play_tune = True   # or False to disable sounds
# (connect/arm/close paths in the code play short cues if enabled)
```

Tone strings are QBasic-style and compatible with ArduPilot’s tone parser.

---

## 🧪 Demo blocks (safe by default)

`main.py` ships with demo sections gated by flags:

* `SAFE_DEMO = False` — full, commented walkthrough (flip to `True` to run).
* A second mini-demo (SITL-friendly) under another `if False:` block.

Both demonstrate connection, info/telemetry, modes, servo/RC, mission helpers, guided controls, and cleanup.

---

## 🧰 Utility: list USB serials (again)

```python
from pixhawkcontroller import find_usb_vid_pid
find_usb_vid_pid()  # prints all USB serial devices with VID/PID/port/description
```

Use this to identify what VID/PID your board exposes on your OS.

---

## 🛡 Safety

* **Test in SITL first** (no props):
  `sim_vehicle.py -v Rover --console --map` (or Copter/Plane).
* Commands like `.arm()`, `.set_servo()`, `.set_rc_pwm()` can move actuators.
* **Flight termination** immediately stops actuators — only for emergencies.

---

## 📘 Examples

### List USB serials (before connecting)

```python
from pixhawkcontroller import find_usb_vid_pid

find_usb_vid_pid()
# → prints dicts with port, vid/pid, location, description
```

### Connect (auto-detect or explicit)

```python
from pixhawkcontroller import FlightControllerInterface

# Auto-detect over USB (uses default VID/PID scanning)
fc = FlightControllerInterface()
fc.connect()

# Or explicit serial:
# fc = FlightControllerInterface(device="COM3", baudrate=115200)            # Windows
# fc = FlightControllerInterface(device="/dev/ttyUSB0", baudrate=115200)    # Linux
# fc = FlightControllerInterface(device="/dev/tty.usbmodem14101", baudrate=115200)  # macOS
# fc.connect()

# Or SITL:
# fc = FlightControllerInterface(device="udp:127.0.0.1:14550"); fc.connect()
```

### Board info & quick telemetry

```python
fc.print_info()      # Vendor/Product, FW/OS git hashes, capabilities, IDs
fc.print_telemetry() # Mode/Family, Armed, GPS fix, Location, Battery
```

### Explicit VID/PID examples

```python
# Bootloader (USB-CDC) — same vendor/product seen on many Pixhawk bootloaders
fc = FlightControllerInterface(vid="1209", pid="5741"); fc.connect()

# Pixhawk 2.4.8 (ST VCP / ChibiOS)
fc = FlightControllerInterface(vid="0483", pid="5740"); fc.connect()

# Cube+ family (CubePilot)
fc = FlightControllerInterface(vid="2DAE", pid="1058"); fc.connect()  # CubeOrange+
# fc = FlightControllerInterface(vid="2DAE", pid="1101"); fc.connect()  # CubeBlack+
```

### Change modes (auto family: copter/plane/rover)

```python
fc.set_mode("GUIDED")
fc.set_mode("AUTO")
fc.set_mode("RTL")
fc.set_mode("SMART_RTL")
```

### Arm / RC override (use with caution)

```python
# Arm only if not already armed
if not fc.check_arm_status():
    fc.arm()  # use fc.arm(force=True) to override prechecks (dangerous)

# Override throttle (ch3) to 1500 µs for 2 seconds, then clear
fc.set_rc_pwm(3, 1500)
import time; time.sleep(2)
fc.clear_rc_overrides()

# Disarm when done
fc.disarm()
```

### Servo control (PWM µs)

```python
import time
fc.set_servo(9, 900);  time.sleep(1.5)
fc.set_servo(9, 1500); time.sleep(1.5)
fc.set_servo(9, 1900)
```

### Relay & Motor test

```python
# Toggle relay #0 → 10 cycles, 2.0 s period
fc.repeat_relay(relay_number=0, count=10, period_s=2.0)

# Run motor #1 at 20% for 3s (type=0 → percent)
fc.motor_test(motor_index=1, throttle_type=0, throttle_value=20.0, duration_s=3.0)
```

### Mission helpers

```python
# Start current mission (set AUTO first)
fc.set_mode("AUTO")
fc.mission_start()

# Pause / continue (in AUTO)
fc.pause_continue_mission(True)
time.sleep(5)
fc.pause_continue_mission(False)
```

### Guided reposition & yaw

```python
# Move in GUIDED to a lat/lon/alt at 3 m/s and auto-switch to GUIDED
lat, lon, alt = 23.911222, 90.254833, 46
fc.do_reposition(lat, lon, alt, speed_m_s=3.0, change_mode_to_guided=True)

# Yaw to heading 90° at 30°/s (absolute)
fc.set_yaw_speed(90.0, 30.0, absolute=True)
```

### Guided limits & condition delay

```python
# Limit GUIDED motion (timeout=60s, horizontal leash=50m)
fc.do_guided_limits(timeout_s=60, horiz_max_m=50)

# Insert a 5s delay (useful inside AUTO missions)
fc.condition_delay(5)
```

### Takeoff / Land / RTL / (Emergency) Termination

```python
# Takeoff to 20m (Copter/Plane; Rover usually ignores)
fc.nav_takeoff(target_alt_m=20.0, min_pitch_deg=0.0)

# Land at current location
fc.nav_land()

# Return To Launch
fc.return_to_launch()

# Emergency stop (cuts actuators immediately) — DANGEROUS
# fc.flight_termination(True)
```

### Rover-specific: reverse direction

```python
# Reverse on, wait, then off (Rover only)
fc.set_reverse(True)
time.sleep(1.0)
fc.set_reverse(False)
```

### Tones (QBasic-style) & optional auto cues

```python
from pixhawkcontroller import TonesQb

# Manual tunes
fc.play_tune(TonesQb.def_tone)
time.sleep(1)
fc.play_tune(TonesQb.twinkle_little_star)

# Optional audible cues for events in your methods
fc.auto_play_tune = True  # set False to silence
```

### Clean shutdown

```python
# Final snapshot then close
fc.print_telemetry()

if fc.check_arm_status():
    fc.disarm()

fc.close()
```

---

## ❓ Troubleshooting

* **No device found / auto-detect fails**: run `find_usb_vid_pid()` and use explicit VID/PID.
  On Linux, add your user to `dialout` and re-log.
* **Mode won’t change**: ensure TX mode switch isn’t overriding; check pre-arm checks and link quality (`STATUSTEXT`).
* **No `AUTOPILOT_VERSION`**: ensure `SERIAL0_PROTOCOL=2` and you’re connected to the MAVLink port.

---

## 📚 References

* [ArduPilot MAVLink Commands & Mission Items](https://ardupilot.org/dev/docs/mavlink-mission-command-messages.html)
* [MAVLink Message Definitions](https://mavlink.io/en/messages/common.html)
* [ArduPilot ToneTester](https://ardupilot.org/dev/docs/code-overview-ardupilot.html#tonetester) (for previewing tunes)

---

## 📜 License

MIT License © 2025 Md Shahriar Forhad
See the [LICENSE](./LICENSE) file for full terms.

---

## ⚠️ Disclaimer

> This software is provided *as-is* for educational and experimental use only.
> Use it at your own risk. The author assumes no liability for any damage, injury, or loss resulting from its use.

```



























from pymavlink.DFReader import DFReader_binary
import tempfile
import os
from collections import defaultdict

error_codes = {
    2: {0: "Errors Resolved", 1: "Late Frame : no updates received from receiver for two seconds"},
    3: {0: "Errors Resolved", 1: "Failed to initialise (probably a hardware issue)", 4: "Unhealthy : failed to read from the sensor"},
    5: {0: "Failsafe Resolved", 1: "Failsafe Triggered"},
    6: {0: "Failsafe Resolved", 1: "Failsafe Triggered"},
    8: {0: "Failsafe Resolved", 1: "Failsafe Triggered"},
    9: {0: "Failsafe Resolved", 1: "Altitude fence breach, Failsafe Triggered", 2: "Circular fence breach, Failsafe Triggered",
        3: "Both Alt and Circular fence breached, Failsafe Triggered", 4: "Polygon fence breached, Failsafe Triggered"},
    10: {0: "Flight mode Change failure: Vehicle was unable to enter the desired flight mode normally because of a bad position estimate"},
    11: {0: "Glitch cleared", 2: "GPS Glitch occurred"},
    12: {1: "Crash into ground detected", 2: "Loss of control detected"},
    13: {2: "Flip abandoned"},
    15: {2: "Not Deployed, vehicle too low", 3: "Not Deployed, vehicle landed"},
    16: {0: "Variance cleared", 2: "Bad Variance"},
    17: {0: "Failsafe Resolved", 1: "Failsafe Triggered"},
    18: {0: "Errors Resolved", 4: "Unhealthy : failed to read from the sensor"},
    19: {0: "Failsafe Resolved", 1: "Failsafe Triggered"},
    20: {0: "Failsafe Resolved", 1: "Report to Pilot", 2: "Avoid by climbing/descending", 3: "Avoid horizontally", 
         4: "Avoid perpendicularly", 5: "RTL invoked"},
    21: {2: "Missing terrain data"},
    22: {2: "Failed to set destination", 3: "RTL restarted", 4: "Circle init failed", 5: "Destination outside fence"},
    23: {0: "Failsafe Resolved", 1: "Failsafe Triggered"},
    24: {0: "1st EKF primary", 1: "2nd EKF primary"},
    25: {0: "Thrust Restored", 1: "Thrust Loss Detected"},
    26: {0: "Sensor Failsafe Cleared", 1: "Sensor Failsafe Triggered"},
    27: {0: "Leak Failsafe Cleared", 1: "Leak Detector Triggered"},
    28: {0: "Pilot Input Failsafe Cleared", 1: "Triggered"},
    29: {0: "Vibration Compensation Deactivated", 1: "Activated"}
}


mode_descriptions = {
    0: "Stabilize",
    1: "Acro",
    2: "AltHold",
    3: "Auto",
    4: "Guided",
    5: "Loiter",
    6: "RTL",
    7: "Circle",
    9: "Land",
    10: "Drift",
    11: "Sport",
    13: "PosHold",
    14: "Brake",
    15: "Throw",
    16: "Avoid_ADSB",
    17: "Guided_NoGPS",
    18: "SmartRTL",
    19: "FlowHold",
    20: "Follow",
    21: "ZigZag",
    22: "SystemID",
    23: "Heli_Autorotate",
    24: "AutoTune",
    25: "Reserved"
}

def parse_bin_file(file_bytes: bytes):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file_bytes)
        tmp.flush()
        tmp_path = tmp.name

    flight_data = defaultdict(dict)

    try:
        mav = DFReader_binary(tmp_path)

        while True:
            msg = mav.recv_msg()
            if msg is None:
                break

            msg_type = msg.get_type()
            time = getattr(msg, 'TimeUS', None)
            if time is None:
                continue

            if msg_type == "MSG" and hasattr(msg, "Message"):
                text = msg.Message.lower()
                if "disarmed" in text:
                    flight_data[time]["Disarmed"] = True
                elif "armed" in text:
                    flight_data[time]["Armed"] = True

            elif msg_type == "GPS":
                if hasattr(msg, "Alt"):
                    flight_data[time]["Altitude"] = msg.Alt
                if hasattr(msg, "Status"):
                    flight_data[time]["GPSFix"] = msg.Status
                if hasattr(msg, "Lat") and hasattr(msg, "Lng"):
                    flight_data[time]["Lat"] = msg.Lat / 1e7
                    flight_data[time]["Lng"] = msg.Lng / 1e7

            elif msg_type == "BAT":
                if hasattr(msg, "Temp"):
                    flight_data[time]["BatteryTemp"] = msg.Temp
                if hasattr(msg, "Volt"):
                    flight_data[time]["BatteryVolt"] = msg.Volt
                if hasattr(msg, "Curr"):
                    flight_data[time]["BatteryCurr"] = msg.Curr

            elif msg_type == "ATT":
                if hasattr(msg, "Roll"):
                    flight_data[time]["Roll"] = msg.Roll
                if hasattr(msg, "Pitch"):
                    flight_data[time]["Pitch"] = msg.Pitch
                if hasattr(msg, "Yaw"):
                    flight_data[time]["Yaw"] = msg.Yaw

            elif msg_type == "VIBE":
                if hasattr(msg, "VibeX"):
                    flight_data[time]["VibeX"] = msg.VibeX
                if hasattr(msg, "VibeY"):
                    flight_data[time]["VibeY"] = msg.VibeY
                if hasattr(msg, "VibeZ"):
                    flight_data[time]["VibeZ"] = msg.VibeZ

            elif msg_type == "MODE":
                mode_code = getattr(msg, "Mode", None)
                mode_name = mode_descriptions.get(mode_code, "Unknown")
                flight_data[time]["Mode"] = mode_name

            elif msg_type == "ERR" and hasattr(msg, "ECode") and hasattr(msg, "Subsys"):
                code_desc = error_codes.get(msg.Subsys, {}).get(msg.ECode)

                if "Errors" not in flight_data[time]:
                    flight_data[time]["Errors"] = []

                flight_data[time]["Errors"].append({
                    "Subsys": msg.Subsys,
                    "ECode": msg.ECode,
                    "Description": code_desc or "Unknown Error",
                })

                if msg.Subsys == 28 and msg.ECode == 1:
                    flight_data[time]["RCSignalLoss"] = True

        return flight_data

    finally:
        os.remove(tmp_path)
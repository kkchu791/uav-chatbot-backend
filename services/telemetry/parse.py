# services/telemetry/parse.py

from pymavlink.DFReader import DFReader_binary
import tempfile
import os

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

def parse_bin_file(file_bytes: bytes):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file_bytes)
        tmp.flush()
        tmp_path = tmp.name

    try:
        mav = DFReader_binary(tmp_path)

        altitudes = []
        battery_temps = []
        gps_fixes = []
        mode_changes = []
        critical_errors = []

        while True:
            msg = mav.recv_msg()
            if msg is None:
                break

            msg_type = msg.get_type()
            time = getattr(msg, 'TimeUS', None)

            if msg_type == "GPS":
                if hasattr(msg, "Alt"):
                    altitudes.append((msg.TimeUS, msg.Alt))
                if hasattr(msg, "Status"):
                    gps_fixes.append((msg.TimeUS, msg.Status))

            if msg_type == "MODE":
                mode_changes.append((time, getattr(msg, "Mode", None)))

            if msg_type == "BAT" and hasattr(msg, "Temp"):
                battery_temps.append((msg.TimeUS, msg.Temp))

            if msg_type == "ERR" and hasattr(msg, "ECode") and hasattr(msg, "Subsys"):
                code_desc = error_codes.get(msg.Subsys, {}).get(msg.ECode)
                if code_desc:
                    critical_errors.append({
                        "TimeUS": time,
                        "Subsys": msg.Subsys,
                        "ECode": msg.ECode,
                        "Description": code_desc
                    })

        return {
            "altitudes": altitudes,
            "gps_fix_statuses": gps_fixes,
            "battery_temps": battery_temps,
            "mode_changes": mode_changes,
            "critical_errors": critical_errors
        }

    finally:
        os.remove(tmp_path)
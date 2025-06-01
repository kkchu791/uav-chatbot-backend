from pymavlink.DFReader import DFReader_binary
import csv
import tempfile
import os

telemetry_data = {}

error_codes = {
    2: {
        0: "Errors Resolved",
        1: "Late Frame : no updates received from receiver for two seconds"
    },
    3: {
        0: "Errors Resolved",
        1: "Failed to initialise (probably a hardware issue)",
        4: "Unhealthy : failed to read from the sensor"
    },
    5: {
        0: "Failsafe Resolved",
        1: "Failsafe Triggered"
    },
    6: {
        0: "Failsafe Resolved",
        1: "Failsafe Triggered"
    },
    8: {
        0: "Failsafe Resolved",
        1: "Failsafe Triggered"
    },
    9: {
        0: "Failsafe Resolved",
        1: "Altitude fence breach, Failsafe Triggered",
        2: "Circular fence breach, Failsafe Triggered",
        3: "Both Alt and Circular fence breached, Failsafe Triggered",
        4: "Polygon fence breached, Failsafe Triggered"
    },
    10: {
        0: "Flight mode Change failure: Vehicle was unable to enter the desired flight mode normally because of a bad position estimate"
    },
    11: {
        0: "Glitch cleared",
        2: "GPS Glitch occurred"
    },
    12: {
        1: "Crash into ground detected. Normally vehicle is disarmed soon after",
        2: "Loss of control detected. Normally parachute is released soon after"
    },
    13: {
        2: "Flip abandoned (not armed, pilot input or timeout)"
    },
    15: {
        2: "Not Deployed, vehicle too low",
        3: "Not Deployed, vehicle landed"
    },
    16: {
        0: "Variance cleared (position estimate OK)",
        2: "Bad Variance (position estimate bad)"
    },
    17: {
        0: "Failsafe Resolved",
        1: "Failsafe Triggered"
    },
    18: {
        0: "Errors Resolved",
        4: "Unhealthy : failed to read from the sensor"
    },
    19: {
        0: "Failsafe Resolved",
        1: "Failsafe Triggered (normally vehicle disarms)"
    },
    20: {
        0: "Failsafe Resolved",
        1: "No action just report to Pilot",
        2: "Vehicle avoids by climbing or descending",
        3: "Vehicle avoids by moving horizontally",
        4: "Vehicle avoids by moving perpendicular to other vehicle",
        5: "RTL invoked"
    },
    21: {
        2: "Missing terrain data"
    },
    22: {
        2: "Failed to set destination",
        3: "RTL restarted",
        4: "Circle initialisation failed",
        5: "Destination outside fence"
    },
    23: {
        0: "Failsafe Resolved",
        1: "Failsafe Triggered (normally vehicle RTLs)"
    },
    24: {
        0: "1st EKF has become primary",
        1: "2nd EKF has become primary"
    },
    25: {
        0: "Thrust Restored",
        1: "Thrust Loss Detected (altitude may be prioritised over yaw control)"
    },
    26: {
        0: "Sensor Failsafe Cleared",
        1: "Sensor Failsafe Triggered"
    },
    27: {
        0: "Leak Failsafe Cleared",
        1: "Leak Detector Failsafe Triggered"
    },
    28: {
        0: "Pilot Input Failsafe Cleared",
        1: "Pilot Input Failsafe Triggered"
    },
    29: {
        0: "Excessive Vibration Compensation De-activated",
        1: "Excessive Vibration Compensation Activated"
    }
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

            # Altitude
            if msg_type == "GPS" and hasattr(msg, "Alt") and hasattr(msg, "TimeUS"):
                altitudes.append((msg.TimeUS, msg.Alt))

            # GPS Fix Quality
            if msg_type == "GPS" and hasattr(msg, "Status") and hasattr(msg, "TimeUS"):
                gps_fixes.append((msg.TimeUS, msg.Status))

            # Mode change
            if msg_type == "MODE":
                mode_changes.append((time, getattr(msg, "Mode", None)))

            # Battery Temperature
            if msg_type == "BAT" and hasattr(msg, "Temp") and hasattr(msg, "TimeUS"):
                battery_temps.append((msg.TimeUS, msg.Temp))

            # Critical error
            if msg_type == "ERR" and hasattr(msg, "ECode"):
                if msg.Subsys in error_codes and msg.ECode in error_codes[msg.Subsys]:
                    critical_errors.append({
                        "TimeUS": time,
                        "Subsys": getattr(msg, "Subsys", None),
                        "ECode": getattr(msg, "ECode", None),
                        "Description": error_codes[msg.Subsys][msg.ECode]
                    })

        return {
            "altitudes": altitudes,
            "gps_fix_statuses": gps_fixes,
            "battery_temps": battery_temps,
            "mode_changes": mode_changes,
            "critical_errors": critical_errors,
        }
    finally:
        os.remove(tmp_path)
    
def store_real_telemetry_in_csv(file_bytes):
    parsed = parse_bin_file(file_bytes)
    write_to_csv(parsed)


def write_to_csv(data):
    # Altitudes
    with open("new_altitudes.csv", mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["TimeUS", "Altitude"])
        for time, alt in data["altitudes"]:
            writer.writerow([time, alt])

    # GPS Fixes
    with open("new_gps_fixes.csv", mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["TimeUS", "GPS Fix Status"])
        for time, status in data["gps_fix_statuses"]:
            writer.writerow([time, status])

    # Mode Changes
    with open("new_mode_changes.csv", mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["TimeUS", "Mode"])
        for time, mode in data["mode_changes"]:
            writer.writerow([time, mode])
    
    # Battery Temps
    with open("new_battery_temps.csv", mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["TimeUS", "Battery Temperature"])
        for time, temp in data["battery_temps"]:
            writer.writerow([time, temp])

    # Critical Errors
    with open("new_critical_errors.csv", mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["TimeUS", "Subsys", "ECode", "Description"])
        writer.writeheader()
        for error in data["critical_errors"]:
            writer.writerow(error)

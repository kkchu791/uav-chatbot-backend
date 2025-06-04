
import csv

def write_telemetry_to_csv(data: dict):
    write_altitudes(data.get("altitudes", []))
    write_gps_fixes(data.get("gps_fix_statuses", []))
    write_mode_changes(data.get("mode_changes", []))
    write_battery_temps(data.get("battery_temps", []))
    write_critical_errors(data.get("critical_errors", []))

def write_altitudes(altitudes):
    with open("new_altitudes.csv", mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["TimeUS", "Altitude"])
        writer.writerows(altitudes)

def write_gps_fixes(gps_fixes):
    with open("new_gps_fixes.csv", mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["TimeUS", "GPS Fix Status"])
        writer.writerows(gps_fixes)

def write_mode_changes(mode_changes):
    with open("new_mode_changes.csv", mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["TimeUS", "Mode"])
        writer.writerows(mode_changes)

def write_battery_temps(battery_temps):
    with open("new_battery_temps.csv", mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["TimeUS", "Battery Temperature"])
        writer.writerows(battery_temps)

def write_critical_errors(errors):
    with open("new_critical_errors.csv", mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["TimeUS", "Subsys", "ECode", "Description"])
        writer.writeheader()
        for row in errors:
            writer.writerow(row)
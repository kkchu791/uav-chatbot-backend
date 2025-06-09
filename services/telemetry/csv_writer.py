import csv

def write_telemetry_to_csv(flight_data: dict, filename="flight_summary.csv"):
    fieldnames = set()
    for entry in flight_data.values():
        fieldnames.update(entry.keys())
    fieldnames = ["TimeUS"] + sorted(fieldnames)

    sorted_times = sorted(flight_data.keys())

    with open(filename, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for time in sorted_times:
            row = {"TimeUS": time}
            row.update(flight_data[time])
            writer.writerow(row)
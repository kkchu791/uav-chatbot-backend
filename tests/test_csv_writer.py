import csv
from services.telemetry.csv_writer import write_telemetry_to_csv

def test_write_telemetry_to_csv_creates_valid_csv(tmp_path):
    flight_data = {
        100: {"Altitude": 1200, "Mode": "Auto"},
        200: {"Altitude": 1400, "BatteryVolt": 12.3}
    }

    output_file = tmp_path / "flight_summary.csv"

    write_telemetry_to_csv(flight_data, filename=str(output_file))

    with open(output_file, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert reader.fieldnames == ["TimeUS", "Altitude", "BatteryVolt", "Mode"]
    assert rows[0]["TimeUS"] == "100"
    assert rows[0]["Altitude"] == "1200"
    assert rows[0]["Mode"] == "Auto"
    assert rows[0]["BatteryVolt"] == ""

    assert rows[1]["TimeUS"] == "200"
    assert rows[1]["Altitude"] == "1400"
    assert rows[1]["BatteryVolt"] == "12.3"
    assert rows[1]["Mode"] == ""
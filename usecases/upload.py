from services.telemetry.parse import parse_bin_file
from services.telemetry.csv_writer import write_telemetry_to_csv
from models.session_registry import session_registry
from services.llm.openai_client import client
from pathlib import Path

def handle_upload(file_bytes: bytes, session_id: str):
    parsed = parse_bin_file(file_bytes)
    write_telemetry_to_csv(parsed)

    file_paths = [
        "new_altitudes.csv",
        "new_critical_errors.csv",
        "new_gps_fixes.csv",
        "new_mode_changes.csv",
        "new_battery_temps.csv"
    ]

    uploaded_files = [
        client.files.create(file=Path(path), purpose="assistants")
        for path in file_paths
    ]

    session = session_registry.find_or_create(session_id)
    session.update(file_ids=[f.id for f in uploaded_files])
    session_registry.save_sessions()
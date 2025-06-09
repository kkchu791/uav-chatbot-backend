from services.telemetry.parse import parse_bin_file
from services.telemetry.csv_writer import write_telemetry_to_csv
from models.session_registry import session_registry
from services.llm.openai_client import client
from pathlib import Path

def handle_upload(file_bytes: bytes, session_id: str):
    parsed = parse_bin_file(file_bytes)
    summary_path = "flight_summary.csv"
    write_telemetry_to_csv(parsed, summary_path)

    uploaded_file = client.files.create(file=Path(summary_path), purpose="assistants")

    session = session_registry.find_or_create(session_id)
    session.update(file_ids=[uploaded_file.id])
    session_registry.save_sessions()
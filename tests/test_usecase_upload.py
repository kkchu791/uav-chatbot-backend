from unittest.mock import patch, MagicMock
from usecases.upload import handle_upload

def test_handle_upload_basic_flow():
    file_bytes = b"some binary data"
    session_id = "test-session-id"

    # Fake parsed telemetry
    parsed_data = {
        "altitudes": [(1, 100)],
        "gps_fix_statuses": [(1, 1)],
        "mode_changes": [(1, "AUTO")],
        "battery_temps": [(1, 40)],
        "critical_errors": [{"TimeUS": 1, "Subsys": 2, "ECode": 1, "Description": "Late Frame"}],
    }

    fake_file_ids = [f"file-{i}" for i in range(5)]
    fake_uploaded_files = [MagicMock(id=fid) for fid in fake_file_ids]
    fake_session = MagicMock()

    with patch("usecases.upload.parse_bin_file", return_value=parsed_data), \
         patch("usecases.upload.write_telemetry_to_csv") as write_csv, \
         patch("usecases.upload.client.files.create", side_effect=fake_uploaded_files), \
         patch("usecases.upload.session_registry.find_or_create", return_value=fake_session), \
         patch("usecases.upload.session_registry.save_sessions") as save_sessions:

        handle_upload(file_bytes, session_id)

        write_csv.assert_called_once_with(parsed_data)
        fake_session.update.assert_called_once_with(file_ids=fake_file_ids)
        save_sessions.assert_called_once()
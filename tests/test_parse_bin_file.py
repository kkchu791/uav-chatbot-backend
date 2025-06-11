from unittest.mock import patch
from services.telemetry.parse import parse_bin_file

# Simulates real MAVLink messages with normal attribute behavior
class FakeMsg:
    def __init__(self, msg_type, **kwargs):
        self._type = msg_type
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_type(self):
        return self._type

@patch("services.telemetry.parse.DFReader_binary")
def test_parse_bin_file_full_coverage(mock_reader):
    mock_msg_1 = FakeMsg("MSG", TimeUS=100, Message="Armed")
    mock_msg_2 = FakeMsg("MSG", TimeUS=101, Message="Disarmed")
    mock_msg_3 = FakeMsg("GPS", TimeUS=102, Alt=1200, Status=3, Lat=123456789, Lng=987654321)
    mock_msg_4 = FakeMsg("BAT", TimeUS=103, Temp=45, Volt=12.5, Curr=3.2)
    mock_msg_5 = FakeMsg("ATT", TimeUS=104, Roll=1.1, Pitch=2.2, Yaw=3.3)
    mock_msg_6 = FakeMsg("VIBE", TimeUS=105, VibeX=0.1, VibeY=0.2, VibeZ=0.3)
    mock_msg_7 = FakeMsg("MODE", TimeUS=106, Mode=3)
    mock_msg_8 = FakeMsg("ERR", TimeUS=107, Subsys=28, ECode=1)
    mock_msg_9 = None

    mock_instance = mock_reader.return_value
    mock_instance.recv_msg.side_effect = [
        mock_msg_1, mock_msg_2, mock_msg_3, mock_msg_4, mock_msg_5,
        mock_msg_6, mock_msg_7, mock_msg_8, mock_msg_9
    ]

    result = parse_bin_file(b"fake-bytes")

    print(result, 'result')

    assert result[100]["Armed"] is True
    assert result[101]["Disarmed"] is True
    assert result[102]["Altitude"] == 1200
    assert result[102]["GPSFix"] == 3
    assert result[102]["Lat"] == 12.3456789
    assert result[102]["Lng"] == 98.7654321
    assert result[103]["BatteryTemp"] == 45
    assert result[103]["BatteryVolt"] == 12.5
    assert result[103]["BatteryCurr"] == 3.2
    assert result[104]["Roll"] == 1.1
    assert result[104]["Pitch"] == 2.2
    assert result[104]["Yaw"] == 3.3
    assert result[105]["VibeX"] == 0.1
    assert result[105]["VibeY"] == 0.2
    assert result[105]["VibeZ"] == 0.3
    assert result[106]["Mode"] == "Auto"
    assert result[107]["RCSignalLoss"] is True
    assert result[107]["Errors"][0]["Description"] == "Triggered"
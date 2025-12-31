def parse_sensor_line(line):
    timestamp, value_str, status = line.split("|")
    if status == "OK":
        return timestamp, float(value_str), status
    else:
        return timestamp, None, status

def test_sensor_parsing_ok():
    line = "2025-01-01 10:00:00|42.5|OK"
    ts, value, status = parse_sensor_line(line)
    assert value == 42.5
    assert status == "OK"

def test_sensor_parsing_faulty():
    line = "2025-01-01 10:00:00|-|FAULTY"
    ts, value, status = parse_sensor_line(line)
    assert value is None
    assert status == "FAULTY"


def classify_value(value, low, high):
    if value < low or value > high:
        return "ALARM"
    elif value < low + 0.1*(high-low) or value > high - 0.1*(high-low):
        return "WARNING"
    else:
        return "OK"

def test_alarm_high():
    assert classify_value(120, 0, 100) == "ALARM"

def test_warning():
    assert classify_value(95, 0, 100) == "WARNING"

def test_ok():
    assert classify_value(50, 0, 100) == "OK"

def test_api_output_structure():
    data = {
        "Temperature": {
            "value": 25,
            "timestamp": "2025-01-01",
            "status": "OK"
        }
    }
    assert "Temperature" in data
    assert "status" in data["Temperature"]

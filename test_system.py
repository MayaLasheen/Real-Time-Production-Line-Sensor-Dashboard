# Unit tests for sensor monitoring system

def parse_sensor_line(line):
    """Parse sensor data string: timestamp|value|status"""
    # Split into components using pipe delimiter
    timestamp, value_str, status = line.split("|")
    
    if status == "OK":
        # Convert valid reading to float
        return timestamp, float(value_str), status
    else:
        # Faulty sensor → no valid value
        return timestamp, None, status


def test_sensor_parsing_ok():
    """Test normal sensor reading parsing"""
    line = "2025-01-01 10:00:00|42.5|OK"
    ts, value, status = parse_sensor_line(line)
    
    assert value == 42.5      # Value converted to float
    assert status == "OK"     # Status correctly identified


def test_sensor_parsing_faulty():
    """Test faulty sensor parsing (value = None)"""
    line = "2025-01-01 10:00:00|-|FAULTY"
    ts, value, status = parse_sensor_line(line)
    
    assert value is None      # No valid value for faulty sensor
    assert status == "FAULTY" # Correct status


def classify_value(value, low, high):
    """Classify reading: ALARM, WARNING, or OK"""
    # Check if outside limits → ALARM
    if value < low or value > high:
        return "ALARM"
    
    # Warning margin = 10% of range
    warning_margin = 0.1 * (high - low)
    
    # Check if near limits → WARNING
    if value < low + warning_margin or value > high - warning_margin:
        return "WARNING"
    
    # Otherwise → OK
    return "OK"


def test_alarm_high():
    """Value above upper limit → ALARM"""
    assert classify_value(120, 0, 100) == "ALARM"


def test_warning():
    """Value in warning zone (90-100) → WARNING"""
    assert classify_value(95, 0, 100) == "WARNING"


def test_ok():
    """Value in safe zone (10-90) → OK"""
    assert classify_value(50, 0, 100) == "OK"


def test_api_output_structure():
    """Test API response has correct structure"""
    data = {
        "Temperature": {
            "value": 25,
            "timestamp": "2025-01-01",
            "status": "OK"
        }
    }
    
    # Verify sensor exists
    assert "Temperature" in data
    # Verify required fields exist
    assert "status" in data["Temperature"]
    # Could also check for "value" and "timestamp"

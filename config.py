# config.py
SENSOR_LIMITS = {
    "Temperature": (-10, 80),
    "Vibration": (0, 50),
    "Speed": (0, 1200),
    "Pressure": (900, 1100),
    "Current": (0, 5)
}

SENSOR_PORTS = {
    "Temperature": 5001,
    "Vibration": 5002,
    "Speed": 5003,
    "Pressure": 5004,
    "Current": 5005,
}

EMAIL = {
    "enabled": False,  # CHANGE TO TRUE FOR TESTING
    "sender": "mayalasheen29@gmail.com",
    "recipient": "mayalasheen29@gmail.com",
    "app_password": "kxof vfwv wybf dhyp",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 465
}

ALERTS = {
    "email_throttle_seconds": 300,
    "plot_buffer_size": 40
}

API = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": False
}

# TCP Sensor Monitoring System

## Overview
This project implements a Python-based monitoring system designed for a production line environment.  
The system monitors multiple sensors concurrently, updates their readings in real time, detects abnormal conditions, and triggers alarms, notifications, and emails when limits are exceeded.

Each sensor communicates over TCP and provides:
- Current value
- Timestamp
- Sensor status (OK or FAULTY)

The system includes a graphical user interface (GUI), an alarm logging mechanism, sensor simulators, and basic support for remote data access.

---

## Features
- Real-time monitoring of multiple sensors
- Concurrent sensor handling using threads
- Explicit sensor status handling (OK / FAULTY)
- Alarm detection (above limits, below limits, faulty)
- Alarm log window with save and clear functionality
- Email throttling to avoid notification spam
- Mute and acknowledge alarm functionality
- Real-time plots with rolling data windows
- TCP-based sensor simulation

---

## Project Structure
- main.py  
  Main GUI application and system logic

- gui.py  
  Generated GUI layout from Qt Designer

- alarm_log_window.py  
  Generated Alarm Log layout from Qt Designer

- alarm_log.py  
  Alarm log window logic

- sensor_worker.py  
  Threaded TCP sensor client implementation

- tcp_sensor_simulator.py  
  TCP-based sensor data simulator

- test_system.py  
  Basic unit tests for core logic

---

## System Architecture

### Sensor Simulation
Each sensor is simulated using a TCP server running on a unique port.  
The simulator periodically sends messages containing:
- Sensor value
- Timestamp
- Sensor status

This allows realistic testing of normal operation, alarm conditions, and sensor faults.

### Sensor Workers
Each sensor is handled by a dedicated SensorWorker thread.  
This ensures:
- Sensors run concurrently
- The GUI remains responsive
- Thread-safe communication using PyQt signals

---

## Alarm Handling
An alarm is triggered when:
- The sensor value exceeds defined limits
- The sensor reports a FAULTY status

Alarm states are logged with:
- Timestamp
- Sensor name
- Value
- Alarm type

Notifications and emails are sent only if:
- The system is not muted
- The alarm is not acknowledged

Additionally, for emails specifically:
- To prevent spamming engineers, email notifications are throttled:
  - Each sensor has its own last-email timestamp
  - A new email is sent only if at least 5 minutes have passed since the last one

---

## Alarm Log Window
The alarm log window provides:
- A table of historical alarms
- Save functionality to export alarms to CSV
- Clear functionality to reset the log
- Acknowledge button to suppress repeated alerts

---

## Real-Time Plotting
Each sensor has a dedicated plot showing recent values:
- Rolling window of the last 40 samples
- Threshold lines indicating safe limits
- Automatic updates as new data arrives

---

## Remote Data Access
The system exposes a simple API interface (via Flask) that allows:
- Accessing current sensor readings
- Accessing overall system status remotely

This enables integration with external systems or dashboards.

---

## Unit Testing
Basic unit tests are included to verify:
- Sensor data parsing
- Alarm detection logic
- API output format

Tests are written using pytest and focus on core system logic rather than GUI components.

---

## Running the Project

### Step 1: Start Sensor Simulators
Run the sensor simulator to start all simulated sensors: 
python tcp_sensor_simulator.py


### Step 2: Start the Main Application
Launch the GUI application:
python main.py


---

## Requirements
- Python 3.x
- PyQt5
- pyqtgraph
- Flask
- pytest

---

## Notes
- Sensor IP addresses are set to localhost for simulation
- In a real deployment, sensor IPs should be updated to actual device addresses
- Each sensor uses a unique TCP port to allow independent connections

---



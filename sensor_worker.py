## Receives Data

from PyQt5.QtCore import QThread, pyqtSignal
import socket
from datetime import datetime

# SensorWorker inherits QThread, and hence it is a QThread 
# (with extra features I add). Each sensor equals one thread,
# hence they run concurrently.
class SensorWorker(QThread): 
    # This defines a signal with a fixed data format:
    # sensor_name, value, timestamp, status.
    # pyqtSignal ensures thread-safe communication.
    data_ready = pyqtSignal(str, float, str, str)

    def __init__(self, sensor_name, host, port, low, high):
        super().__init__()
        self.sensor_name = sensor_name
        self.host = host # IP address / domain name
        self.port = port
        self.low = low
        self.high = high
        self.running = True  # Without this flag, theards would run forever.

    # Runs in a separate OS thread, not the GUI thread.
    def run(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # This is a blocking call → belongs in a thread
            sock.connect((self.host, self.port))
            # Prevents permanent blocking. If sensor stops responding → timeout → fault detection
            sock.settimeout(3.0)

            while self.running:
                try:
                    # .strip() removes the invisible white spaces.
                    line = sock.recv(1024).decode().strip()
                    if not line:
                        raise ValueError("Empty packet")
                    
                    timestamp, value_str, status = line.split("|")
                    
                    if status == "OK":
                        value = round(float(value_str),2)
                    else:
                        value = 0.00
                except Exception:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    value = 0.0
                    status = "FAULTY"
    
                # Sends data thread-safely, Qt queues the signal.
                # GUI receives it in the main thread.                
                self.data_ready.emit(
                    self.sensor_name,
                    value,
                    timestamp,
                    status
                )
        # Handles disconnections, parse errors (data in the wrong format), timeouts.
        except Exception:
            self.data_ready.emit(
                self.sensor_name,
                0.0,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "FAULTY"
            )
    # Clean Shutdown
    def stop(self):
        self.running = False
        self.wait()

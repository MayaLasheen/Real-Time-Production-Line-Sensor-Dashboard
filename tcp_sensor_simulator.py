## Generates Data

import socket
import random
import time
from datetime import datetime


# one function = one sensor
def start_sensor(port, low, high):
    # AF_INET: IPv4, and SOCK_STREAM: TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("localhost", port))
    
    # 1 = max queued clients. This is what makes a server.
    # Each sensor is meant to talk to one monitoring system
    s.listen(1)
    print(f"Sensor running on port {port}")

    # Blocking line --> wait until a client connects
    conn, _ = s.accept() # Returns connection socket, and client address.
    
    while True:
        # Simulate random sensor failure
        # if random.random() < 0.1:
        #     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #     conn.sendall(f"{timestamp}|-|FAULTY\n".encode())
        #     time.sleep(2)
        #     continue
    
        value = random.uniform(low - 1, high + 1)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # TCP has no message boundaries — newline is critical
        conn.sendall(f"{timestamp}|{value}|OK\n".encode())
  
        time.sleep(0.5) # Sensor update rate = 2 Hz, therefore time.sleep should be 0.5 s



if __name__ == "__main__":
    sensors = [
        (5001, -10, 80),
        (5002, 0, 50),
        (5003, 0, 1200),
        (5004, 900, 1100),
        (5005, 0, 5),
    ]

    for port, low, high in sensors:
        import threading
        threading.Thread(
            target=start_sensor, args=(port, low, high), daemon=True
        ).start()

    while True:
        time.sleep(1)

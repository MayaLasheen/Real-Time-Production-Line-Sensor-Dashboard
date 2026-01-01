## Displays Data

from PyQt5 import QtWidgets, QtCore, QtGui
from gui import Ui_MainWindow
from alarm_log_window import AlarmLogWindow
import sys
import pyqtgraph as pg
from collections import deque
from sensor_worker import SensorWorker
import time
import smtplib
from email.mime.text import MIMEText
from flask import Flask, jsonify
import threading
import math


from config import (
    SENSOR_LIMITS, 
    SENSOR_PORTS, 
    EMAIL, 
    ALERTS, 
    API
)

from maintenance_console import MaintenanceConsoleUI
from maintenance_console_controller import MaintenanceConsoleController
from system_logger import SystemLogger


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Create alarm log window once
        self.alarm_log_window = AlarmLogWindow()

        self.init_plots()

        # Connect button
        self.ui.button.clicked.connect(self.show_alarm_log)
        self.muted = False  # Mutes all tray/email notifications
        self.ui.pushButton_mute.clicked.connect(self.toggle_mute)
        
        self.sensor_names = list(SENSOR_LIMITS.keys())
        self.workers = []
        
        
        
        
        for name in self.sensor_names:
        
            # Creates a thread per sensor.    
            worker = SensorWorker(
                sensor_name=name,
                # host is set to localhost for simulation purposes, where
                # the sensor is simulated on the same PC. However, in production,
                # it should be changed to the actual sensor IP address.
                host="localhost",
                port=SENSOR_PORTS[name],
                low=SENSOR_LIMITS[name][0],
                high=SENSOR_LIMITS[name][1]
            )
        
            # Thead to GUI communication.
            worker.data_ready.connect(self.update_sensor_from_thread)
            
            # Launches the thread.
            worker.start()
            self.workers.append(worker)

        # Non-blocking notification system
        self.tray = QtWidgets.QSystemTrayIcon(self)
        icon = QtGui.QIcon("icon.png")
        self.tray.setIcon(icon)        

        self.tray.setVisible(True)
        self.tray.setToolTip("Sensor Monitoring System")
        
        
        # Tray menu
        # Create an empty menu
        tray_menu = QtWidgets.QMenu()
        # Add "Acknowledge All Alarms" option
        ack_action = tray_menu.addAction("Acknowledge All Alarms")
        ack_action.triggered.connect(self.acknowledge_all_alarms)
        
        tray_menu.addSeparator()
        
        # Add "Exit" option
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(QtWidgets.QApplication.quit)
        
        # Attach this menu to the tray icon
        # (Right-clicking the tray icon will show this menu)
        self.tray.setContextMenu(tray_menu)

        
        # Alarm acknowledgment state
        # It stores the sensor names that have been acknlowedged, where set is an unordered collection of unique elements.
        self.acknowledged_alarms = set()
        self.last_email_time = {}  # {sensor_name: timestamp}
        self.email_throttle_seconds = ALERTS["email_throttle_seconds"]
        

        # Stores latest sensor states for API access
        # Thread-safe because GUI thread updates it.
        self.api_sensor_data = {
            name: {
                "value": None,
                "timestamp": None,
                "status": "UNKNOWN"
            }
            for name in self.sensor_names
        }

        # Logger
        self.logger = SystemLogger()
        
        # Maintenance Console
        self.maintenance_ui = MaintenanceConsoleUI()
        self.maintenance_controller = MaintenanceConsoleController(
            ui=self.maintenance_ui,
            main_window=self,
            logger=self.logger
        )
        
        # Connect logger to console
        self.logger.log_event.connect(self.maintenance_ui.log_view.append)
        
        # Optional button to open console
        self.ui.button_maintenance.clicked.connect(self.maintenance_ui.show)


    def show_alarm_log(self):
        self.alarm_log_window.show()


    def update_sensor_from_thread(self, sensor_name, value, timestamp, status):
        
        row = self.sensor_names.index(sensor_name)
    
        if status == "FAULTY":
            self.update_sensor_faulty(row, timestamp)
        else:
            self.update_sensor_reading(row, value, timestamp)
    
        self.update_status()
        
        # Update API-visible data
        self.api_sensor_data[sensor_name] = {
            "value": value,
            "timestamp": timestamp,
            "status": status
        }
        
    
    def update_sensor_reading(self, row, value, timestamp):
        sensor_name = self.ui.tableWidget.item(row, 0).text()
    
        # Update timestamp & value in table
        self.ui.tableWidget.item(row, 1).setText(timestamp)
        self.ui.tableWidget.item(row, 2).setText(str(value))
    

    
        low, high = SENSOR_LIMITS[sensor_name]
        range_span = high - low
        warning_margin = 0.1 * range_span
    
        warn_low = low + warning_margin
        warn_high = high - warning_margin
    
        # Decide status BASED ON VALUE ONLY
        if value < low or value > high:
            status = "ALARM"
            color = QtGui.QColor(255, 200, 200)
            self.logger.log(
                f"{sensor_name} ALARM: value={value}"
            )
            
            if not self.muted:
                if sensor_name not in self.acknowledged_alarms:
                    # Notify
                    self.tray.showMessage(
                        f"{sensor_name} Alarm",
                        f"{sensor_name} value is out of range.",
                        QtWidgets.QSystemTrayIcon.Critical,
                        3000
                    )   
                    
                    # Email
                    now = time.time()
                    last_sent = self.last_email_time.get(sensor_name, 0)
                    
                    # Avoids throttling emails
                    if now - last_sent > self.email_throttle_seconds:
                        self.last_email_time[sensor_name] = now      
                        QtCore.QThreadPool.globalInstance().start(
                            lambda: send_email("ALARM", f"{sensor_name} readings are out of range.")
                        )
            # else:
            #     print("Muted")
            # log
            if value < low:
                self.alarm_log_window.add_alarm(
                    timestamp, sensor_name, value, "BELOW LIMIT"
                )
                
            else:
                self.alarm_log_window.add_alarm(
                    timestamp, sensor_name, value, "ABOVE LIMIT"
                )
                
                
    
        elif value < warn_low or value > warn_high:
            status = "WARNING"
            color = QtGui.QColor(255, 255, 200)
    
        else:
            status = "OK"
            color = QtGui.QColor(200, 255, 200)
            if sensor_name in self.acknowledged_alarms:
                self.acknowledged_alarms.remove(sensor_name)
    
        # Update table status
        self.ui.tableWidget.item(row, 3).setText(status)
    
        for col in range(4):
            self.ui.tableWidget.item(row, col).setBackground(color)
    
        # Update plot
        self.update_plot(sensor_name, value)


    def update_sensor_faulty(self, row, timestamp):
        sensor_name = self.ui.tableWidget.item(row, 0).text()
    
        self.ui.tableWidget.item(row, 1).setText(timestamp)
        self.ui.tableWidget.item(row, 2).setText("-")
        self.ui.tableWidget.item(row, 3).setText("FAULTY")
    
        color = QtGui.QColor(255, 200, 200)
        for col in range(4):
            self.ui.tableWidget.item(row, col).setBackground(color)
            
        self.alarm_log_window.add_alarm(
            timestamp, sensor_name, "-", "FAULTY"
        )

        self.logger.log(
            f"{sensor_name} reported FAULTY"
        )
        
        if not self.muted and sensor_name not in self.acknowledged_alarms:
            # Notification
            self.tray.showMessage(
                "Sensor Fault",
                f"{sensor_name} reported FAULTY",
                QtWidgets.QSystemTrayIcon.Critical,
                3000
            )
            # Email
            now = time.time()
            last_sent = self.last_email_time.get(sensor_name, 0)
            
            # Avoids throttling emails
            if now - last_sent > self.email_throttle_seconds:
                self.last_email_time[sensor_name] = now              
                QtCore.QThreadPool.globalInstance().start(
                    lambda: send_email("ALARM", f"{sensor_name} readings are out of range.")
                )
        self.update_plot(sensor_name, math.nan)        


    def update_status(self):
        has_warning = False
    
        for row in range(self.ui.tableWidget.rowCount()):
            status_item = self.ui.tableWidget.item(row, 3)
            
            if not status_item:
                continue
    
            status = status_item.text()
    
            if status == "FAULTY":
                self.ui.label.setText("Overall System Status : FAULTY")
                self.ui.label.setStyleSheet("color: red; font-weight: bold;")
                return   # Highest priority → exit immediately
    
            elif status == "ALARM":
                self.ui.label.setText("Overall System Status : ALARM")
                self.ui.label.setStyleSheet("color: red; font-weight: bold;")
                return   # Next highest priority → exit immediately
    
            elif status == "WARNING":
                has_warning = True
    
        # No alarms found
        if has_warning:
            self.ui.label.setText("Overall System Status : WARNING")
            self.ui.label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.ui.label.setText("Overall System Status : OK")
            self.ui.label.setStyleSheet("color: green; font-weight: bold;")

    def init_plots(self):
        self.plots = {}
        self.plot_curves = {}
        self.plot_buffers = {}
        self.threshold_lines = {}
    
        plot_configs = {
            "Temperature": self.ui.plot_tmp,
            "Vibration": self.ui.plot_vibs,
            "Speed": self.ui.plot_speed,
            "Pressure": self.ui.plot_pressure,
            "Current": self.ui.plot_curr,
        }
    
        for name, container in plot_configs.items():
            plot = pg.PlotWidget()
            plot.setBackground("w")
            plot.setTitle(name)
            plot.showGrid(x=True, y=True)
            plot.setLabel("left", "Value")
            plot.setLabel("bottom", "Time (samples)")
    
            layout = QtWidgets.QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(plot)
    
            curve = plot.plot(pen=pg.mkPen(width=2))
    
            self.plots[name] = plot
            self.plot_curves[name] = curve
            # rolling window
            # window_duration = sample_rate × buffer_length
            self.plot_buffers[name] = deque(
                maxlen=ALERTS["plot_buffer_size"]
            ) 

            low, high = SENSOR_LIMITS[name]

            low_line = pg.InfiniteLine(pos=low, angle=0, pen=pg.mkPen('b', width=2))
            high_line = pg.InfiniteLine(pos=high, angle=0, pen=pg.mkPen('b', width=2))

            plot.addItem(low_line)
            plot.addItem(high_line)

    def update_plot(self, sensor_name, value):
        buffer = self.plot_buffers[sensor_name]
        buffer.append(value)
    
        y = list(buffer)
        x = list(range(len(y)))  # sample index
    
        self.plot_curves[sensor_name].setData(x, y)
             
                                      
    

        
    def closeEvent(self, event):
        for worker in self.workers:
            worker.stop()
        event.accept()

    

            
    def acknowledge_all_alarms(self):
        for row in range(self.ui.tableWidget.rowCount()):
            sensor = self.ui.tableWidget.item(row, 0).text()
            status = self.ui.tableWidget.item(row, 3).text()
    
            if status in ("ALARM", "FAULTY"):
                self.acknowledged_alarms.add(sensor)
    
        self.tray.showMessage(
            "Alarms Acknowledged",
            "Notifications suppressed until alarm clears",
            QtWidgets.QSystemTrayIcon.Information,
            2000
        )

        self.logger.log("All alarms acknowledged by operator")


    
        
    def toggle_mute(self):
        self.muted = not self.muted
        if self.muted:
            self.ui.pushButton_mute.setText("Unmute")
        else:
            self.ui.pushButton_mute.setText("Mute")
        state = "MUTED" if self.muted else "UNMUTED"
        self.logger.log(f"Notifications {state}")

        
def send_email(subject, body):
    # Skip if email disabled
    if not EMAIL["enabled"]:
        print("Email notifications are disabled in config")
        return
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL["sender"]
    msg["To"] = EMAIL["recipient"]

    # Passowrd should be the 16-character app password, NOT your regular password
    with smtplib.SMTP_SSL(
        EMAIL["smtp_server"], 
        EMAIL["smtp_port"]
    ) as server:
        server.login(
            EMAIL["sender"], 
            EMAIL["app_password"]
        )
        server.send_message(msg)

def start_api(main_window):
    """
    Starts a Flask web API server to expose sensor data and system status.
    This allows external applications to access real-time monitoring data via HTTP.
    
    Args:
        main_window: Reference to the main application window containing sensor data
    """
    
    # Create Flask application instance
    app = Flask(__name__)
    
    # Define endpoint: /api/sensors
    @app.route("/api/sensors")
    def sensors():
        """
        API endpoint that returns current sensor data in JSON format.
        Accessible via: GET http://<server-ip>:5000/api/sensors
        """
        # Convert sensor data dictionary to JSON response
        return jsonify(main_window.api_sensor_data)
    
    # Define endpoint: /api/status
    @app.route("/api/status")
    def status():
        """
        API endpoint that returns overall system status.
        Accessible via: GET http://<server-ip>:5000/api/status
        """
        return jsonify({
            "overall_status": main_window.ui.label.text()  # Get status text from UI label
        })
    
    # Start the Flask web server
    app.run(
        host=API["host"],  # Listen on all network interfaces (accessible from other devices)
        port=API["port"],       # Standard Flask development port
        debug=API["debug"]      # Disable debug mode for production use
    )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()
    
    # Start REST API in background thread
    api_thread = threading.Thread(
        target=start_api,
        args=(window,),
        daemon=True
    )
    api_thread.start()

    sys.exit(app.exec_())

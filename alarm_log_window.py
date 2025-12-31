from PyQt5.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout
from PyQt5 import QtWidgets
from alarm_log import Ui_AlarmLog
import csv

class AlarmLogWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_AlarmLog()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.clear_alarms)
        self.ui.pushButton_2.clicked.connect(self.save_alarms)


    def add_alarm(self, time, sensor, value, alarm_type):
        row = self.ui.alarmTable.rowCount()
        self.ui.alarmTable.insertRow(row)

        self.ui.alarmTable.setItem(row, 0, QTableWidgetItem(time))
        self.ui.alarmTable.setItem(row, 1, QTableWidgetItem(sensor))
        self.ui.alarmTable.setItem(row, 2, QTableWidgetItem(str(value)))
        self.ui.alarmTable.setItem(row, 3, QTableWidgetItem(alarm_type))

    def clear_alarms(self):
        self.ui.alarmTable.setRowCount(0)
        
    def save_alarms(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Alarm Log", "", "CSV Files (*.csv)"
        )
    
        if not path:
            return
    
        with open(path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Time", "Sensor", "Value", "Type"])
    
            for row in range(self.ui.alarmTable.rowCount()):
                row_data = []
                for col in range(self.ui.alarmTable.columnCount()):
                    item = self.ui.alarmTable.item(row, col)
                    row_data.append(item.text() if item else "")
                writer.writerow(row_data)



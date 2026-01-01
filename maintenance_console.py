from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QTextEdit, QLineEdit, QLabel, QApplication
)

class MaintenanceConsoleUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maintenance Console")

        layout = QVBoxLayout()

        # Access control
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.unlock_button = QPushButton("Unlock")

        # Log viewer
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)

        # Remote commands
        self.clear_alarms_button = QPushButton("Clear Alarms")
        self.snapshot_button = QPushButton("Request Snapshot")

        # Disabled until authenticated
        self.clear_alarms_button.setEnabled(False)
        self.snapshot_button.setEnabled(False)

        layout.addWidget(QLabel("Maintenance Password"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.unlock_button)
        layout.addWidget(self.log_view)
        layout.addWidget(self.clear_alarms_button)
        layout.addWidget(self.snapshot_button)

        self.setLayout(layout)

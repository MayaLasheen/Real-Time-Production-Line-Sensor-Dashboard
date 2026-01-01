class MaintenanceConsoleController:
    def __init__(self, ui, main_window, logger):
        self.ui = ui
        self.main = main_window
        self.logger = logger

        # Connect UI actions
        self.ui.unlock_button.clicked.connect(self.authenticate)
        self.ui.clear_alarms_button.clicked.connect(self.clear_alarms)
        self.ui.snapshot_button.clicked.connect(self.request_snapshot)

    def authenticate(self):
        if self.ui.password_input.text() == "admin123":
            self.ui.clear_alarms_button.setEnabled(True)
            self.ui.snapshot_button.setEnabled(True)
            self.logger.log("Maintenance console unlocked")
        else:
            self.logger.log("Failed maintenance login attempt")

    def clear_alarms(self):
        self.main.alarm_log_window.clear_alarms()
        self.logger.log("All alarms cleared by maintenance")

    def request_snapshot(self):
        # self.logger.log("Snapshot requested")
        # for row in range(self.main.ui.tableWidget.rowCount()):
        #     sensor = self.main.ui.tableWidget.item(row, 0).text()
        #     value = self.main.ui.tableWidget.item(row, 2).text()
        #     status = self.main.ui.tableWidget.item(row, 3).text()
        #     self.logger.log(f"{sensor}: value={value}, status={status}")
        # self.logger.log("Snapshot ended")
        self.main.alarm_log_window.save_alarms()
        self.logger.log("All alarms saved by maintenance")
        
    
        

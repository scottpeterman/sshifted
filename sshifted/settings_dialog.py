import yaml
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton

class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Application Style Setting
        style_layout = QHBoxLayout()
        self.style_combo = QComboBox()
        self.style_combo.addItems(["fusion", "windows"])
        self.style_combo.setCurrentText(self.settings.get('application_style', 'fusion'))
        style_layout.addWidget(QLabel("Application Style:"))
        style_layout.addWidget(self.style_combo)
        layout.addLayout(style_layout)

        # Show Welcome Tab Setting
        welcome_layout = QHBoxLayout()
        self.welcome_combo = QComboBox()
        self.welcome_combo.addItems(["true", "false"])
        self.welcome_combo.setCurrentText(str(self.settings.get('show_welcome_tab', True)).lower())
        welcome_layout.addWidget(QLabel("Show Welcome Tab:"))
        welcome_layout.addWidget(self.welcome_combo)
        layout.addLayout(welcome_layout)

        # Save and Cancel Buttons
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.saveSettings)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

    def saveSettings(self):
        self.settings['application_style'] = self.style_combo.currentText()
        self.settings['show_welcome_tab'] = self.welcome_combo.currentText() == 'true'
        with open('settings_editor.yaml', 'w') as file:
            yaml.dump(self.settings, file)
        self.accept()
import os
import sys

import yaml
from PyQt6 import QtWidgets
from PyQt6.QtCore import QUrl, QTimer, QEvent
from PyQt6.QtGui import QShortcut, QKeySequence, QPalette
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QVBoxLayout, QTextBrowser, QPushButton, QDialog, \
    QStyleFactory
from sshifted.EditorMenuSystem import EditorMenu as EditorMenuSystem
from sshifted.Library.editor import Editor
from sshifted.settings_dialog import SettingsDialog

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About SShifted Editor")
        self.resize(400, 300)
        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout(self)
        text_browser = QTextBrowser(self)
        text_browser.setHtml("""
        <h1>SShifted, a Multi-Tabbed Editor</h1>
        <p>Version: 0.1.0</p>
        <br><a href = "https://github.com/scottpeterman/sshifted">https://github.com/scottpeterman/sshifted</a>
        <p>This application is a multi-tabbed text editor based on Ace and PyQt6</p>
        <p>For more information about Ace, visit the <a href="https://ace.c9.io/">Ace official website</a>.
        <p>For more information about PyQt Bindings for Qt, visit the <a href="https://www.riverbankcomputing.com/">Riverbank Computing</a>.
        <p>For more information about Qt, visit the <a href="https://www.qt.io/">Qt Group</a>.
        </p>
        <p>SSHifted Text Editor is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
        """)
        text_browser.setOpenExternalLinks(True)
        layout.addWidget(text_browser)
        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

class MainApplication(QMainWindow):
    def __init__(self, settings):
        super().__init__()
        self.editors = {}
        self.settings = settings
        self.setWindowTitle("SShifted Text Editor")
        self.resize(800, 600)
        self.initializeUI()
        self.initializeMenuSystem()
        self.initializeShortcuts()
        self.parent_app = None

    def initializeUI(self):
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.closeTab)
        self.tabs.currentChanged.connect(self.updateStatusBar)  # Connect tab change signal
        self.setCentralWidget(self.tabs)
        self.statusBar = self.statusBar()  # Initialize status bar
        # self.addTab()
        # self.addTab(tab_type="welcome")
        if self.settings['show_welcome_tab']:
            self.addTab(tab_type="welcome")
        else:
            self.addTab(tab_type="new")

    def initializeMenuSystem(self):
        self.menuSystem = EditorMenuSystem(self)
        self.menuSystem.newFileRequested.connect(self.newFile)
        self.menuSystem.openFileRequested.connect(self.openFile)  # Connect to the new slot
        self.menuSystem.saveFileRequested.connect(self.saveFile)
        self.menuSystem.saveFileAsRequested.connect(self.saveFileAs)
        self.menuSystem.settingsRequested.connect(self.openSettingsDialog)
        self.menuSystem.aboutRequested.connect(self.openAboutDialog)
        self.menuSystem.uiThemeChanged.connect(self.changeUITheme)
        self.menuSystem.aceThemeChanged.connect(self.changeAceEditorTheme)

    def changeUITheme(self, theme_name):
        new_style = QStyleFactory.create(theme_name)
        if self.parent_app is not None:
            self.parent_app.setStyle(new_style)
            new_palette = QPalette(new_style.standardPalette())
            self.parent_app.setPalette(new_palette)

    def changeAceEditorTheme(self, theme_name):
        current_editor = self.getCurrentEditor()
        if isinstance(current_editor, Editor):
            current_editor.changeEditorTheme(theme_name)

    def openSettingsDialog(self):
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.applySettings()

    def applySettings(self):
        # Re-apply settings, e.g., change style
        # app = QtWidgets.QApplication.instance()
        if self.parent_app is not None:
            new_style = QStyleFactory.create(self.settings['application_style'])
            self.parent_app.setStyle(new_style)
            new_palette = QPalette(new_style.standardPalette())
            self.parent_app.setPalette(new_palette)



    def openAboutDialog(self):
        # Implement the logic to open the about dialog
        about_dialog = AboutDialog(self)
        about_dialog.exec()
        # ... Connect other signals ...
    def getCurrentEditor(self):
        return self.tabs.currentWidget()

    def cutText(self):
        editor = self.getCurrentEditor()
        if isinstance(editor, Editor):
            editor.cutText()

    def copyText(self):
        editor = self.getCurrentEditor()
        if isinstance(editor, Editor):
            editor.copyText()

    def pasteText(self):
        editor = self.getCurrentEditor()
        if isinstance(editor, Editor):
            editor.pasteText()

    def selectAllText(self):
        editor = self.getCurrentEditor()
        if isinstance(editor, Editor):
            editor.selectAllText()


    def addTab(self, file_path=None, tab_type="new"):
        if tab_type == "existing" and file_path:
            if file_path and any(tab.file_path == file_path for tab in self.editors.values()):
                QMessageBox.warning(self, "File Already Open",
                                    f"The file '{os.path.basename(file_path)}' is already open.",
                                    QMessageBox.StandardButton.Ok)
                return
            tab = Editor(self)
            self.editors[tab.editorId] = tab
            tab.fileSaved.connect(self.updateTabTitle)
            if file_path:
                tab.loadFile(file_path)  # Load the file into the Editor
                tab.has_changed = False
            else:
                tab.new_file = True

            # Use a default value if not set

            tab_title = os.path.basename(file_path) if file_path else "New File"
            index = self.tabs.addTab(tab, tab_title)
            # Make the tab closable
            editor_theme = self.settings.get('editor_theme', 'monokai')
            tab.changeEditorTheme(editor_theme)
            QTimer.singleShot(1000, lambda: tab.changeEditorTheme(editor_theme))
            self.tabs.setCurrentIndex(index)  # Activate the new tab
            self.updateStatusBar(index)
        elif tab_type == "welcome":
            # New behavior for the welcome tab
            current_dir = os.path.dirname(__file__)
            print(f"current dir: {current_dir}")
            splash_html_path = os.path.join(current_dir, 'ace', 'splash.html')
            print(f"loading: {splash_html_path}")
            welcome_tab = QWebEngineView()
            welcome_tab.load(QUrl.fromLocalFile(splash_html_path))
            index = self.tabs.addTab(welcome_tab, "Welcome")
            self.tabs.setCurrentIndex(index)
            self.updateStatusBar(index)
        else:
            # Default to creating a new file tab
            tab = Editor(self)
            self.editors[tab.editorId] = tab
            tab.fileSaved.connect(self.updateTabTitle)
            tab.new_file = True
            tab_title = "New File"
            index = self.tabs.addTab(tab, tab_title)
            self.tabs.setCurrentIndex(index)
            self.updateStatusBar(index)
            editor_theme = self.settings.get('editor_theme', 'monokai')
            tab.changeEditorTheme(editor_theme)
            QTimer.singleShot(1000, lambda: tab.changeEditorTheme(editor_theme))

    def closeEvent(self, event: QEvent):
        # Check if there are any tabs other than the welcome tab
        open_editor_tabs = any(isinstance(self.tabs.widget(i), Editor) for i in range(self.tabs.count()))

        if open_editor_tabs:
            # Prompt the user to confirm they want to close
            reply = QMessageBox.question(self, 'Exit', 'You have open tabs. Are you sure you want to exit without saving?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                event.accept()  # The user confirmed they want to close
            else:
                event.ignore()  # The user chose not to close
        else:
            event.accept()  # No editor tabs open, so close without prompting

    def updateTabTitle(self, file_path):
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, Editor):
            index = self.tabs.indexOf(current_tab)
            tab_title = os.path.basename(file_path)
            self.tabs.setTabText(index, tab_title)

    def closeTab(self, index):
        editor = self.tabs.widget(index)
        if isinstance(editor, Editor) and editor.has_changed:
            reply = QMessageBox.question(self, "Save File",
                                         "This file has unsaved changes. Do you want to save before closing?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)

            if reply == QMessageBox.StandardButton.Yes:
                if editor.file_path:
                    editor.requestSave()  # Save the existing file
                else:
                    editor.requestSaveAs()  # Prompt 'Save As' if it's a new file
            elif reply == QMessageBox.StandardButton.Cancel:
                return  # Cancel closing the tab

        self.tabs.removeTab(index)

    def saveFileAs(self):
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, Editor):
            current_tab.requestSaveAs()

    def openFile(self, file_path):
        # Open and load the file in a new tab
        self.addTab(file_path, tab_type="existing")
        self.statusBar.showMessage(f"Opened file: {file_path}")


    def updateStatusBar(self, index):
        tab = self.tabs.widget(index)
        if tab and isinstance(tab, Editor):
            file_status = tab.file_path if tab.file_path else "** New File **"
            self.statusBar.showMessage(file_status)

    def newFile(self):
        self.addTab()
        # Implement new file logic

    def initializeShortcuts(self):
        newFileShortcut = QShortcut(QKeySequence('Ctrl+N'), self)
        newFileShortcut.activated.connect(self.newFile)  # Connect to your newFile method

    def saveFile(self):
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, Editor):
            current_tab.requestSave()
            # ... Implement other slot methods ...

def load_or_create_settings(file_path, default_settings):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            yaml.dump(default_settings, file)
        return default_settings
    else:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)

def main():
    # print(f"Debug webengine here: http://127.0.0.1:9222/")
    # print("cli python uglyeditor.py --webEngineArgs --remote-debugging-port=9222 --remote-allow-origins=http://127.0.0.1:9222")

    settings_file = 'settings_editor.yaml'
    default_settings = {
        'application_style': 'fusion',
        'show_welcome_tab': True
    }

    settings = load_or_create_settings(settings_file, default_settings)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(settings['application_style'])
    app.setStyleSheet("""
   
QMenu::icon {
    margin: 0px;
    padding: 0px;
    width: 0px; /* Hide the icon by setting the width to 0 */
}
    """)

    main_window = MainApplication(settings)
    main_window.show()
    main_window.parent_app = app
    sys.exit(app.exec())

if __name__ == "__main__":
    print(f"Debug webengine here: http://127.0.0.1:9222/")
    main()

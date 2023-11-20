from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QFileDialog


class EditorMenuSystem(QObject):
    newFileRequested = pyqtSignal()
    openFileRequested = pyqtSignal(str)
    saveFileRequested = pyqtSignal()
    saveFileAsRequested = pyqtSignal()
    settingsRequested = pyqtSignal()
    aboutRequested = pyqtSignal()


    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupMenus(parent)

    def setupMenus(self, parent):
        menu_bar = parent.menuBar()
        file_menu = menu_bar.addMenu("&File")
        self.addMenuAction(file_menu, "&New", self.newFile)  # Call newFile method on trigger
        self.addMenuAction(file_menu, "&Open...", self.openFile)  # Call openFile method on trigger

        self.addMenuAction(file_menu, "&Save", self.saveFileRequested)
        self.addMenuAction(file_menu, "Save &As...", self.saveFileAsRequested)
        file_menu.addSeparator()
        self.addMenuAction(file_menu, "E&xit", parent.close)

        # Add Options Menu
        options_menu = menu_bar.addMenu("&Options")
        self.addMenuAction(options_menu, "&Settings", self.settings)

        # Add Help Menu
        help_menu = menu_bar.addMenu("&Help")
        self.addMenuAction(help_menu, "&About", self.about)


    def addMenuAction(self, menu, title, method):
        action = QAction(title, self)
        action.triggered.connect(method)  # Connect to a method
        menu.addAction(action)

    def newFile(self):
        self.newFileRequested.emit()


    def openFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self.parent(), "Open File", "", "All Files (*)")
        if file_path:
            self.openFileRequested.emit(file_path)

    def saveFile(self):
        self.saveFileRequested.emit()

    def saveFileAs(self):
        self.saveFileAsRequested.emit()

    def settings(self):
        self.settingsRequested.emit()

    def about(self):
        self.aboutRequested.emit()

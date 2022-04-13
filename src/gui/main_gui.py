from PyQt5 import QtWidgets

# importing libraries
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import time
from gui.language_select import LanguageSelectWidget
from gui.recording_window import RecordingWidget
from app.record import Recorder
from gui.form import FormWindow
from win32api import GetSystemMetrics


class MainWindow(QMainWindow):
    #EXIT_CODE_REBOOT = -12345678 

    def __init__(self) -> None:
        super().__init__()
        self.restart_recording()
        self.setGeometry(100, 100, 800, 500)

    
    def restart_recording(self):
        self.main_widget = MainWidget(parent=self)
        self.setCentralWidget(self.main_widget)




class MainWidget(QWidget):
     
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.recorder = Recorder()
        self.UI()
        

    def UI(self):
        layout = QVBoxLayout()
        self.language_window = LanguageSelectWidget(parent=self)

        self.form_window = FormWindow(parent=self)
        layout.addWidget(self.form_window)

        layout.addWidget(self.language_window)
        self.language_window.hide()

        self.restart_button = QPushButton("Start New Recording Session")
        self.restart_button.adjustSize()
        self.restart_button.clicked.connect(self.parent().restart_recording)
        layout.addWidget(self.restart_button)
        self.restart_button.hide()

        self.setLayout(layout)
        
        #self.setGeometry(0, 0, GetSystemMetrics(0), GetSystemMetrics(1))
        self.setWindowTitle('PyQt5 Layout')
        self.show()
        #self.showMaximized()


    def on_form_complete(self, info):
        self.recorder.set_info_participant(info)
        self.form_window.hide()
        self.language_window.show()


    def set_recording_window(self, language):
        self.language_window.hide()
        self.recorder.set_language(language)
        self.recording_window = RecordingWidget(parent=self, language=language)
        self.layout().addWidget(self.recording_window)


    def recording_finished(self):
        print("Finished all recordings")
        self.recording_window.destroy()
        self.layout().removeWidget(self.recording_window)
        self.restart_button.show()


    



def main():

    a = QApplication(sys.argv)
    font = QFont("Arial", 14)
    a.setFont(font)
    w = MainWindow()
    #w.showMaximized()
    w.show()
    currentExitCode = a.exec_()


    

if __name__ == "__main__":
    main()
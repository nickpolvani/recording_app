from PyQt5 import QtWidgets

# importing libraries
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
from app.player_recorder import PlayerRecorder, DatasetType
from gui.choose_dataset_window import ChooseDatasetWindow
from gui.playing_window import PlayerRecordingWidget

class MainWindow(QMainWindow):

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
        self.player_recorder = PlayerRecorder(main_widget=self)
        self.choose_ds_window = ChooseDatasetWindow(parent=self)
        self.recording_window = PlayerRecordingWidget(parent=self)
        self.UI()
        

    def UI(self):
        layout = QVBoxLayout()

        self.setLayout(layout)
        layout.addWidget(self.choose_ds_window)
        layout.addWidget(self.recording_window)
        self.recording_window.hide()

        self.setWindowTitle('')
        self.show()


    def on_dataset_selected(self, ds_type:DatasetType):
        self.player_recorder.set_dataset_type(ds_type=ds_type)
        self.choose_ds_window.hide()
        self.recording_window.show()


    def get_rec_num(self) -> int:
        return self.player_recorder.current_recording


    def finished_recording(self, next_recording):
        self.recording_window.update_recording_num(next_recording)


def main():

    a = QApplication(sys.argv)
    font = QFont("Arial", 26)
    a.setFont(font)
    w = MainWindow()
    w.show()
    #w.showMaximized()
    currentExitCode = a.exec_()


    

if __name__ == "__main__":
    main()
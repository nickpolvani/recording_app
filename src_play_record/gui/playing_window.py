


import sys
import time
from PyQt5.QtWidgets import QListWidget, QWidget, QVBoxLayout, QLabel, QPushButton
from gui.main import MainWidget

class PlayerRecordingWidget(QWidget):
    def __init__(self, parent:MainWidget):
        super().__init__(parent)

        self.num_track_label = QLabel()
        self.num_track_label.setText(f"Num Track: {self.parent().get_rec_num()}")

        self.start_button = QPushButton("Start Play/Record")
        self.start_button.clicked.connect(self._start_recording)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self._stop_recording)
        self.UI()

    
    def UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.num_track_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        self.stop_button.hide()
        self.setLayout(layout)
        self.show()


    def _start_recording(self):
        self.start_button.hide()
        self.stop_button.show()
        self.parent().player_recorder.start_playing_loop()


    def _stop_recording(self):
        self.parent().player_recorder.stop_playing_loop()
        self.start_button.show()
        self.stop_button.hide()



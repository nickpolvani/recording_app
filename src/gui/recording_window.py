
import sys
import time
from PyQt5.QtWidgets import QListWidget, QWidget, QVBoxLayout, QLabel, QPushButton

from app.get_text import TextProvider


class RecordingWidget(QWidget):
    def __init__(self, parent:QWidget, language:str):
        super().__init__(parent)
        self.language = language
        self.max_recordings = 3
        self.num_recordings = 0

        self.title_label = QLabel()
        self.title_label.setText(f"Recording Window for: {self.language}")

        self.start_rec_button = QPushButton("Start Recording")
        self.start_rec_button.adjustSize()
        self.start_rec_button.clicked.connect(self.start_recording)

        self.stop_rec_button = QPushButton("Stop Recording")
        self.stop_rec_button.adjustSize()
        self.stop_rec_button.clicked.connect(self.stop_recording)

        self.text_panel = QLabel()
        self.text_panel.setText("Text to read")

        
        self.text_provider = TextProvider(language)
        self.UI()
        

    def UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.text_panel)
        layout.addWidget(self.start_rec_button)
        layout.addWidget(self.stop_rec_button)
        self.stop_rec_button.hide()
        self.text_panel.hide()
        self.setLayout(layout)
        self.show()


    def start_recording(self):
        print("Recording...")
        self.num_recordings += 1
        self.title_label.setText(f"Recording {self.num_recordings}/{self.max_recordings}")
        self.start_rec_button.hide()
        self.stop_rec_button.show()
        text_to_read = self.text_provider.get_paragraph()
        self.text_panel.setText(text_to_read)
        self.text_panel.show()

        self.parent().recorder.start_recording()



    def stop_recording(self):
        print("Stop recording...")

        self.start_rec_button.show()
        self.stop_rec_button.hide()
        self.text_panel.hide()
        self.parent().recorder.stop_recording()

        if self.num_recordings >= self.max_recordings:
            self.parent().recording_finished()



    def destroy(self):
        self.hide()
        self.deleteLater()
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel,
                              QVBoxLayout, QFormLayout, QLineEdit, QComboBox)
import sys
import time
from app.player_recorder import DatasetType



class ChooseDatasetWindow(QWidget):
    def __init__(self, parent:QWidget):
        super().__init__(parent)
        self.dataset_selection = QComboBox()
        self.dataset_selection.addItem("Noise")
        self.dataset_selection.addItem("Speech")

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.on_confirm)

        self.UI()


    def UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.dataset_selection)
        layout.addWidget(self.confirm_button)
        self.setLayout(layout)
        self.show()


    def on_confirm(self):
        ds_type_str = self.dataset_selection.currentText()
        if ds_type_str == "Noise":
            ds_type = DatasetType.NOISE
        elif ds_type_str == "Speech":
            ds_type = DatasetType.SPEECH
        else:
            raise ValueError("Invalid dataset type:", ds_type_str)
        
        self.parent().on_dataset_selected(ds_type)

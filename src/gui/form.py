from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel,
                              QVBoxLayout, QFormLayout, QLineEdit, QComboBox)
import sys
import time





class FormWidget(QWidget):
    def __init__(self, parent:QWidget):
        super().__init__(parent)

        self.first_name_field = QLineEdit()
        self.last_name_field = QLineEdit()
        self.gender_selection = QComboBox()
        self.gender_selection.addItem("Male")
        self.gender_selection.addItem("Female")
        self.gender_selection.addItem("Other")

        self.UI()

    
    def UI(self):
        layout = QFormLayout()
        layout.addRow("First Name:", self.first_name_field)
        layout.addRow("Last Name:", self.last_name_field)
        layout.addRow("Gender:", self.gender_selection)
        self.setLayout(layout)
        self.show()



    def get_error_msg(self) -> str:
        """ returns empty string if there is no error, otherwise an error message"""
        if len(self.first_name_field.text()) == 0:
            return "First Name cannot be empty"
        if len(self.last_name_field.text()) == 0:
            return "Last Name cannot be empty"
        if len(self.gender_selection.currentText()) == 0:
            return "Select a gender"
        return ""


    def get_inputs(self) -> dict:
        """ returns dictionary containing keys: name, last_name, gender. Values are None if not selected """
        participant_info = {
            "first_name": self.first_name_field.text(),
            "last_name": self.last_name_field.text(),
            "gender": self.gender_selection.currentText(),
        }
        return participant_info
    
    


class FormWindow(QWidget):
    def __init__(self, parent:QWidget):
        super().__init__(parent)
        self.form = FormWidget(parent=self)
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.adjustSize()
        self.confirm_button.clicked.connect(self.on_confirm)
        self.error_message_panel = QLabel()
        self.UI()

    def UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.form)
        layout.addWidget(self.confirm_button)
        layout.addWidget(self.error_message_panel)
        self.setLayout(layout)
        self.show()

    def on_confirm(self):
        error_msg = self.form.get_error_msg()
        if len(error_msg) > 0:
            self.error_message_panel.setText(error_msg)
        else:
            info = self.form.get_inputs()
            self.parent().on_form_complete(info)


    def destroy(self):
        self.hide()
        self.deleteLater()

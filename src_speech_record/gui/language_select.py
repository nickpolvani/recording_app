

import sys
import time
from PyQt5.QtWidgets import QListWidget, QWidget, QVBoxLayout, QLabel
from app.get_text import get_available_languages




class LanguageSelectWidget(QWidget):
    def __init__(self, parent:QWidget):
        super().__init__(parent)
        self.UI()
        
    def destroy(self):
        self.hide()
        self.deleteLater()

    def UI(self):
        layout = QVBoxLayout()
        text_label = QLabel()
        text_label.setText("Select a language:")
        layout.addWidget(text_label)

        layout.addWidget(LanguageListWidget(parent=self))
        self.setLayout(layout)
        self.show()



class LanguageListWidget(QListWidget):
 
    def __init__(self, parent:QWidget):
        super().__init__(parent)
        self.UI()

 
    def UI(self):
        languages = get_available_languages()
        for i, language in enumerate(languages):
            self.insertItem(i, language)
        self.clicked.connect(self.language_selected)
        self.show()


    def language_selected(self):
        item_selected = self.currentItem()
        language = item_selected.text()
        self.parent().parent().set_recording_window(language)
        
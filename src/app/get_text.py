
import glob
from pathlib import Path
import random
from tarfile import ENCODING


def get_available_languages() -> list:
    languages = glob.glob("data/*.txt")
    languages = [Path(language).stem for language in languages]
    return languages

ENCODINGS = {
    "dutch": "iso-8859-1",
    "english":  "utf-8",
    "french":  "utf-8",
    "german":  "utf-8",
    "greek":  "utf-8",
    "italian":  "utf-8",
    "polish":  "utf-8",
    "portuguese":  "utf-8",
    "russian":  "utf-8",
    "spanish":  "utf-8",
}


class TextProvider():
    def __init__(self, language:str) -> None:
        self.language = language
        self.max_words = 30
        self.get_sentences()


    def get_sentences(self):
        self.sentences = []
        in_file = open(f"data/{self.language}.txt", "r", encoding=ENCODINGS[self.language])
        for line in in_file:
            self.sentences.append(line)
        in_file.close()


    def get_paragraph(self):
        start_idx = random.randint(0, len(self.sentences) - 4)
        num_words = 0
        out_text = ""
        while num_words < self.max_words or start_idx >= len(self.sentences):
            sentence = self.sentences[start_idx]
            if len(sentence.split()) + num_words > self.max_words:
                sentence = " ".join(sentence.split()[:self.max_words - num_words])
            del self.sentences[start_idx]
            out_text += sentence 
            num_words += len(sentence.split())
        return out_text
"""Fourth version of GUI."""
import librosa
import numpy as np
import pickle
import pyaudio
import random
import re
import soundfile as sf
import threading
import time
import tkinter as tk
import warnings
import wave
import winsound

from argparse import ArgumentParser
from collections import deque
from datetime import datetime
from glob import glob
from operator import itemgetter
# from playsound import playsound
from scipy import signal
from sklearn.preprocessing import MinMaxScaler
from tkinter import ttk

from utils import _find_records, _init_results_folder, _init_root, _input_language, _min_max_scaling, _vad_merge


def parse_args():
    """Parse main arguments."""
    parser = ArgumentParser(description='Main experimental parameters')

    parser.add_argument(
        '-max_blocks', '--max_blocks',
        type=int, default=6,
        help='Total nb of blocks'
    )

    parser.add_argument(
        '-max_sentences', '--max_sentences',
        type=int, default=5,
        help='Total nb of sentences per block'
    )

    parser.add_argument(
        '-rest_time', '--rest_time',
        type=int, default=30,
        help='Rest time between blocks'
    )

    parser.add_argument(
        '-max_audio_duration', '--max_audio_duration',
        type=int, default=10,
        help='In seconds, max duration of random syllable audio'
    )

    parser.add_argument(
        '--no_shuffle',
        default=True, action='store_false',
        help='If data should be shuffled or not prior to the experiment'
    )

    return parser.parse_args()

class App():
    def __init__(
        self,
        root,
        language_idx,
        user_idx,
        shuffle,
        max_blocks,
        max_sentences,
        rest_time,
        max_audio_duration,
        fs=16000,
        channels=2,
        chunk=1024,
    ):
        """
        Main application: inducing cognitive load by a listening-reading dual task.

        root: tk.Tk() object
            Tkinter root

        language_idx: int, 0 or 1
            Language index: 0 for English, 1 for French

        user_idx: int
            Subject index (automatically filled)

        shuffle: bool
            If True, shuffles the reading data before starting the experiment.

        max_blocks: int
            Maximum number of experimental blocks

        rest_time: float
            Rest time between blocks, in seconds

        max_audio_duration: float
            Maximum syllable audio duration, in seconds

        fs: int, default=16000
            Sample rate, in Hz

        channels: int, default=2
            Number of audio channels

        chunk: int, default=1024
            Duration of a chunk, in ms
        """
        self.root = root
        self.root.bind("<space>", self.run_trial)

        self.user_idx = user_idx

        tk.messagebox.showinfo(
            title='Description',
            message='\n'.join([
                'Welcome to the experiment! \n',
                f'The experiment consists of {max_blocks} blocks, with {max_sentences} trials per block. \n',
                'At each block, you will have to read sentences while listening to audio files. \n'
                'To start a trial, hit the SPACEBAR or press "Record", and read your sentences UNTIL THE RECORDING ENDS, while listening and memorizing the number of syllables in the generated audio. \n',
                f'At the end of each block, you will be asked to report the TOTAL number of syllables you heard during the last {max_sentences} trials. \n',
                'To get used to the setup, the first block will serve as a control, without any syllables (only noise).'
            ])
        )

        # Buttons
        self.exit_button = tk.Button(self.root, text='Exit', command=self.root.destroy)
        self.minimize_button = tk.Button(root, text='Mimimize', command=lambda: self.root.wm_state("iconic"))
        self.start_button = tk.Button(self.root, text='Record [SPACEBAR]', command=self.run_trial)

        self.exit_button.pack(side=tk.RIGHT, anchor=tk.NE)
        self.minimize_button.pack(side=tk.RIGHT, anchor=tk.NE)
        self.start_button.pack(pady=(200, 0))

        # Load data
        self.language_idx = language_idx
        self.shuffle = shuffle
        self.sentence_data = self.load_data()
        self.metadata = {}
        self.sentence_text = tk.StringVar()
        self.sentence_text.set(self.log_sentence_info())
        self.sentence_label = tk.Label(self.root, textvariable=self.sentence_text, wraplength=500, font=('Helvetica 24'))
        self.sentence_label.pack(pady=(0, 0))

        # block info
        self.rest_time = rest_time
        self.block_nb = 0
        self.max_blocks = max_blocks
        self.sentence_nb = 0
        self.max_sentences = max_sentences
        self.block_text = tk.StringVar()
        self.block_text.set(self.log_block_info())
        self.block_label = tk.Label(self.root, textvariable=self.block_text, wraplength=500, font=('Helvetica 24'))
        self.block_label.pack()

        # Recording info
        self.fs = fs
        self.channels = channels
        self.chunk = chunk
        self.is_recording = False
        self.frames = []
        self.sample_format = pyaudio.paInt16

        # Progress bar
        self.style = ttk.Style(self.root)
        self.style.layout(
            'text.Horizontal.TProgressbar',
            [
                ('Horizontal.Progressbar.trough', {'children': [('Horizontal.Progressbar.pbar', {'side': 'left', 'sticky': 'ns'})], 'sticky': 'nswe'}),
                ('Horizontal.Progressbar.label', {'sticky': ''})
            ]
        )
        self.style.configure('text.Horizontal.TProgressbar', text=f'Completed: 0/{self.max_sentences * self.max_blocks}')
        self.variable = tk.DoubleVar(self.root)
        self.progress_bar = tk.ttk.Progressbar(
            self.root,
            style='text.Horizontal.TProgressbar',
            mode='determinate',
            length=100,
            variable=self.variable)
        self.progress_bar.pack(pady=100)

        # Load random syllables
        self.max_audio_duration = max_audio_duration
        self.n_syls = self._generate_syl_audio()

    def load_data(self, nb_sentences=3):
        text_fnames = _find_records(language='EN' if self.language_idx == 0 else 'FR')
        if self.shuffle:
            random.shuffle(text_fnames)
        return deque(zip(*(iter(text_fnames),) * nb_sentences))

    def save_metadata(self, now):
        """Save metadata from previous recording."""
        self.metadata[now] = {
            'block': self.block_nb,
            'sentence': self.sentence_nb,
            'text': self.log_sentence_info(),
            'fname': self.sentence_data[0],
            'syls': self.n_syls
        }
        print(self.metadata[now])
        with open(f'results/{self.user_idx}/metadata_{self.user_idx}.pkl', 'wb') as f:
            pickle.dump(self.metadata, f, pickle.HIGHEST_PROTOCOL)

    def _generate_syl_audio(self, padding_mode='awgn'):
        """Generate an audio composed of random syllables played at random intervals."""
        fnames = glob('articulation_index/data/syls/wb/s/*/*.sph')
        n_syls = 0

        max_interval_length = np.random.uniform(3, 6)

        if self.block_nb == 0:
            audio = [np.random.normal(0, 1, self.max_audio_duration * self.fs)]  # only AWGN to begin the trial, no syllables
        else:
            duration = 0
            init_padding_length = random.randint(0, self.fs)
            audio = [np.random.normal(0, 1, init_padding_length)]
            while duration < self.max_audio_duration:
                # Pick a random syllable
                fname = random.choice(fnames)

                # Load and resample to desired SR
                arr, _ = librosa.load(fname, sr=self.fs)

                # Remove silences
                arr = _vad_merge(arr)

                # Scale to [-1, 1]
                arr = _min_max_scaling(arr, a=-1, b=1)

                # Collect current sample
                audio.append(arr)

                # Add some WGN before the next syllable, scaled to [-1, 1]
                padding_length = random.randint(self.fs // 2, int(max_interval_length * self.fs))
                padding_interval = _min_max_scaling(np.random.normal(0, 1, padding_length), a=-1, b=1)
                audio.append(padding_interval)

                # Update counts on total audio duration and number of syllables
                duration = len(np.concatenate(audio, axis=0)) / self.fs
                n_syls += 1

        sf.write('tmp.wav', np.concatenate(audio, axis=0), samplerate=self.fs)
        return n_syls

    def run_trial(self, event=None):
        self.start_recording()
        self.stop_recording()
        self.update(self.record_time)

    def start_recording(self):
        """Start recording."""
        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(
            format=self.sample_format,
            channels=self.channels,
            rate=self.fs,
            frames_per_buffer=self.chunk,
            input=True)

        self.is_recording = True
        self.start_button['state'] = tk.DISABLED
        # self.stop_button['state'] = tk.NORMAL

        print('Recording...')
        t = threading.Thread(target=self.record)
        t.start()

        winsound.PlaySound('tmp.wav', winsound.SND_FILENAME)

    def stop_recording(self):
        """Stop recording."""
        self.is_recording = False
        print('Stopped recording.')
        self.record_time = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")

        wf = wave.open(f'results/{self.user_idx}/{self.record_time}.wav', 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def record(self):
        """Record audio."""
        while self.is_recording:
            data = self.stream.read(self.chunk)
            self.frames.append(data)

    def log_block_info(self):
        """Log info on baseline blocks."""
        return f'Block {self.block_nb+1}/{self.max_blocks}: {self.sentence_nb+1}/{self.max_sentences}'

    def log_sentence_info(self):
        """Log the current reading input."""
        try:
            return '\n'.join([open(sentence, 'rt', encoding='utf-8').read() for sentence in self.sentence_data[0]])
        except UnicodeDecodeError:
            warnings.warn('Error decoding using UTF-8. Using UTF-16', UnicodeWarning)
            return '\n'.join([open(sentence, 'rt', encoding='utf-16').read() for sentence in self.sentence_data[0]])

    def pause(self, count):
        """Launch a countdown for a break between blocks."""
        # change text in label
        self.block_text.set(f'Wait for the next block, have a break ({count} s left)!')
        self.sentence_text.set('')

        if count > 0:
            # call countdown again after 1000 ms (1s)
            self.root.after(1000, self.pause, count - 1)
        else:
            self.block_text.set(self.log_block_info())
            self.sentence_text.set(self.log_sentence_info())

    def reset(self):
        """Reset main values."""
        self.block_text.set(self.log_block_info())
        self.frames = []
        self.sentence_data.popleft()
        self.start_button['state'] = tk.NORMAL
        # self.stop_button['state'] = tk.DISABLED

        self.sentence_text.set(self.log_sentence_info())

    def update(self, now):
        """Update block info."""
        # Save metadata
        self.save_metadata(now)

        if self.sentence_nb + 1 >= self.max_sentences:
            # Ask the user to report his syllable count
            reportingWindow(self.root, self.user_idx, self.n_syls, self.block_nb)

            if self.block_nb + 1 == self.max_blocks:
                # End the experiment.
                print('End of session.')
                self.root.destroy()
                return

            # Initiate a break before next block.
            self.pause(self.rest_time)
            self.block_nb += 1
            self.sentence_nb = 0
            self.n_syls = self._generate_syl_audio()

            self.block_text.set(self.log_block_info())

        else:
            # Go to next setnence
            self.sentence_nb += 1
            self.n_syls += self._generate_syl_audio()

        # Update progress bar (code is very ugly)
        total_nb_trials = self.max_sentences * self.max_blocks
        self.progress_bar.step(100 / (total_nb_trials))
        self.style.configure(
            'text.Horizontal.TProgressbar',
            text=f'Completed: {int(self.variable.get() * (total_nb_trials) / 100)}/{total_nb_trials}')

        # Reset recording parameters and prepare next sentence
        self.reset()

class reportingWindow():
    """Reporting window to ask the user how many syllables he counted."""
    def __init__(self, root, user_idx, n_syls, block_nb):
        self.top = tk.Toplevel(root)
        self.top.attributes('-fullscreen', True)
        self.reporting_label = tk.Label(
            self.top,
            text='How many syllables did you hear in this block?',
            font=('Helvetica 14 bold'))
        self.reporting_label.pack()
        self.reporting_entry_box = tk.Entry(self.top)
        self.reporting_entry_box.pack(pady=(0, 0))

        # self.arousal_label = tk.Label(
        #     self.top,
        #     text='How "emotionally active" did you feel during this block? \n (0: tired/bored/calm, 100: excited/stressed/alert)',
        #     font=('Helvetica 14 bold'))
        # self.arousal_label.pack()
        # self.arousal_scale = tk.Scale(
        #     self.top,
        #     label='',
        #     from_=0,
        #     to=100,
        #     resolution=1,
        #     orient=tk.HORIZONTAL,
        # )
        # self.arousal_scale.pack(pady=(0, 200))

        # self.valence_label = tk.Label(
        #     self.top,
        #     text='How "emotionally positive" did you feeling during this block? \n (0: sad/unhappy, 100: happy/content)',
        #     font=('Helvetica 14 bold'))
        # self.valence_label.pack()

        # self.valence_scale = tk.Scale(
        #     self.top,
        #     label='',
        #     from_=0,
        #     to=100,
        #     resolution=1,
        #     orient=tk.HORIZONTAL,
        # )
        # self.valence_scale.pack(pady=(0, 200))

        self.reporting_button = tk.Button(self.top, text='OK', command=self.quit)
        self.reporting_button.pack()

        self.user_idx = user_idx
        self.n_syls = n_syls
        self.block_nb = block_nb

    def quit(self):
        try:
            pred = int(self.reporting_entry_box.get())
            tk.messagebox.showinfo(
                title='Results',
                message='\n'.join([
                    f'Your prediction: {pred}',
                    f'Solution: {self.n_syls}'
                ])
            )

            # arousal = self.arousal_scale.get()
            # valence = self.valence_scale.get()

            # Dump prediction results in a file
            with open(f'results/{self.user_idx}/reporting_{self.user_idx}_block_{self.block_nb}.pkl', 'wb') as f:
                # pickle.dump({'pred': pred, 'true': self.n_syls, 'arousal': arousal, 'valence': valence}, f, pickle.HIGHEST_PROTOCOL)
                pickle.dump({'pred': pred, 'true': self.n_syls, 'arousal': None, 'valence': None}, f, pickle.HIGHEST_PROTOCOL)

            self.top.destroy()
        except ValueError:
            tk.messagebox.showerror('Invalid input: only integers are allowed.')

if __name__ == '__main__':
    args = parse_args()
    assert args.max_blocks >= 3, "Experiment should have at least 3 blocks"
    # Load data
    language = _input_language()

    # Initiate result folder for current user
    user_idx = _init_results_folder()

    # Create root
    root = _init_root()

    # Run the UI
    app = App(
        root=root,
        language_idx=language,
        user_idx=user_idx,
        max_blocks=args.max_blocks,
        max_sentences=args.max_sentences,
        rest_time=args.rest_time,
        max_audio_duration=args.max_audio_duration,
        shuffle=args.no_shuffle)
    root.mainloop()

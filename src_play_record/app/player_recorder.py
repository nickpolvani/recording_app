from enum import Enum
import os 
import pyaudio 
from scipy.io import wavfile
import wave 
import glob
import time
import shutil
from PyQt5.QtWidgets import QWidget
from pathlib import Path 
import random

from PyQt5.QtCore import QThread
import pandas as pd


# DEBUG
"""
OUT_DEVICE_NAME = "MOTU Audio ASIO" 
IN_DEVICE_NAME = "MOTU Audio ASIO" 

IN_CHANNELS = 4

OUT_CHANNELS = 2

"""

OUT_DEVICE_NAME = "ASUS XG49V (Intel(R) Display Audio)"
IN_DEVICE_NAME =  "Stereo Mix (Realtek HD Audio Stereo input)"

IN_CHANNELS = 2

OUT_CHANNELS = 2

MAX_RECORDING_TIME = 1 * 3600 #seconds

def explore_devices(name):
  # establish index of input device for sound card
  pa = pyaudio.PyAudio()
  for id in range(pa.get_device_count()):
      dev_dict = pa.get_device_info_by_index(id)
      if dev_dict["name"] == name:
        print("Found: ", dev_dict)
        return dev_dict


class DatasetType(Enum):
    SPEECH = "speech"
    NOISE = "noise"


class PlayerRecorder():

    def __init__(self) -> None:
        self.current_recording = 0
        self.save_dir = None
        self.input_dir = None
        self.rate = 44100
        self.in_device_name = IN_DEVICE_NAME
        self.out_device_name = OUT_DEVICE_NAME
        dev_dict = explore_devices(name=self.in_device_name)
        if dev_dict is None:
            raise ValueError(f"Device with name: {self.in_device_name} not found.")
        self.in_device_idx = dev_dict["index"]

        dev_dict = explore_devices(name=self.out_device_name)
        if dev_dict is None:
            raise ValueError(f"Device with name: {self.out_device_name} not found.")
        self.out_device_idx = dev_dict["index"]


        self.in_channels = IN_CHANNELS
        self.out_channels = OUT_CHANNELS
        self.input_filenames = None
        self.pa_record = pyaudio.PyAudio()
        self.pa_play = pyaudio.PyAudio()
        self.recording_time = 0



    def set_dataset_type(self, ds_type:DatasetType):
        self.dataset_type = ds_type 
        df = pd.read_csv("external_recordings/participants.csv")
        num_participant = len(df)
        self.participant_id = num_participant
        self.save_dir = os.path.join("external_recordings", ds_type.value, str(num_participant))
        if not os.path.isdir(self.save_dir):
            os.mkdir(self.save_dir)

        df = df.append({"participant_id": self.participant_id, "ds_type": ds_type.value}, ignore_index=True)
        df.to_csv("external_recordings/participants.csv", index=False)

        if ds_type == DatasetType.NOISE:
            self.input_dir = "audio_datasets/datasets_fullband/noise_fullband"

        elif ds_type == DatasetType.SPEECH:
            self.input_dir = "audio_datasets/datasets_fullband/clean_fullband"

        else:
            raise ValueError("Invalid Dataset Type:", ds_type.name)
        self.input_filenames = list(Path(self.input_dir).rglob("*.wav"))
        random.shuffle(self.input_filenames)



    def _play_callback(self, in_data, frame_count, time_info, status):
        data = self.wf.readframes(frame_count)
        return (data, pyaudio.paContinue)


        
    def start_playing_loop(self):
        self.playing = True
        while self.playing:
            self._start_recording()
            self._start_playing()
            self._stop_playing()
            self._stop_recording()
            print("Current recording:", self.current_recording, "playing time:", self.recording_time)


    def stop_playing_loop(self):
        self.playing = False


    def _start_playing(self):
        self.in_filename = self.input_filenames[self.current_recording]
        self.wf = wave.open(str(self.in_filename), "rb")

        self.recording_time += self.wf.getnframes() / float(self.wf.getframerate())
        if self.recording_time > MAX_RECORDING_TIME:
            self.playing = False

        self.stream_out = self.pa_play.open(format=self.pa_play.get_format_from_width(self.wf.getsampwidth()),
                channels=self.wf.getnchannels(),
                rate=self.wf.getframerate(),
                output=True, 
                output_device_index=self.out_device_idx,
                stream_callback=self._play_callback)

        self.stream_out.start_stream()


    def _stop_playing(self):
        while self.stream_out.is_active():
            time.sleep(0.05)

        self.stream_out.stop_stream()
        self.stream_out.close()
        self.wf.close()

    
    def _record_callback(self, in_data, frame_count, time_info, flag):
        self.fulldata.append(in_data) #saves filtered data in an array
        return (in_data, pyaudio.paContinue)



    def _start_recording(self):
        self.current_recording += 1
        self.format = pyaudio.paInt16
        self.fulldata = []
        
        # DEBUG
        self.pa_record.is_format_supported(rate=48000, #self.rate
                            input_device=self.in_device_idx,
                            input_channels=self.in_channels,
                            input_format=self.format)


        # DEBUG
        self.stream_in = self.pa_record.open(
            rate=48000, #self.rate
            channels=self.in_channels,
            format=self.format,
            input=True,                   # input stream flag
            input_device_index=self.in_device_idx,         # input device index
            frames_per_buffer=1024,
            stream_callback=self._record_callback
        )
        self.stream_in.start_stream()


    def _stop_recording(self):
        self.stream_in.stop_stream()
        self.stream_in.close()
        self._save_recording()



    def _save_recording(self):
        output_dir = os.path.join(self.save_dir, f"{self.current_recording}")
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)

        shutil.copy(self.in_filename, os.path.join(output_dir, "original.wav"))
        output_path = os.path.join(output_dir, "all_channels.wav")
        wav_file = wave.open(output_path, "wb")
        wav_file.setnchannels(self.in_channels)        # number of channels
        wav_file.setsampwidth(self.pa_record.get_sample_size(self.format))        # sample width in bytes
        wav_file.setframerate(self.rate) 
        wav_file.writeframes(b''.join(self.fulldata))
        wav_file.close()

        rate, all_channels = wavfile.read(output_path)

        air_demo_path = os.path.join(output_dir, "air_demo.wav")
        wavfile.write(air_demo_path, rate=rate, data=all_channels[:,0])
        bone_demo_path = os.path.join(output_dir, "bone_demo.wav")
        wavfile.write(bone_demo_path, rate=rate, data=all_channels[:,1])

        # DEBUG
        #air_reference_path = os.path.join(output_dir, "air_reference.wav")
        #wavfile.write(air_reference_path, rate=rate, data=all_channels[:,2])



if __name__ == "__main__":
    player = PlayerRecorder()
    player.set_dataset_type(DatasetType.SPEECH)
    print("Participant:", player.participant_id)
    player.start_playing_loop()
    
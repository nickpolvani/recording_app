import pyaudio 
import wave



def print_all_devices():
  pa = pyaudio.PyAudio()
  for id in range(pa.get_device_count()):
    dev_dict = pa.get_device_info_by_index(id)
    for key, value in dev_dict.items():
        print(key, value)



def explore_devices(name):
  # establish index of input device for sound card
  pa = pyaudio.PyAudio()
  print(pa.get_default_host_api_info())

  for id in range(pa.get_device_count()):
      dev_dict = pa.get_device_info_by_index(id)
      if dev_dict["name"] == name:
        print("Found: ", dev_dict)
        return dev_dict


def record(device_index:int, output_filename:str, length_record=5, rate=44100, channels=2):
    pa = pyaudio.PyAudio()
    format = pyaudio.paInt16


    pa.is_format_supported(rate=rate,
                          input_device=device_index,
                          input_channels=channels,
                          input_format=format)

    stream_in = pa.open(
        rate=rate,
        channels=channels,
        format=format,
        input=True,                   # input stream flag
        input_device_index=device_index,         # input device index
        frames_per_buffer=1024
    )
    print("Start recording")

    # read 5 seconds of the input stream
    input_audio = stream_in.read(length_record * rate)

    print("Done recording")

    wav_file = wave.open(output_filename, 'wb')

    # define audio stream properties
    wav_file.setnchannels(channels)        # number of channels
    wav_file.setsampwidth(pa.get_sample_size(format))        # sample width in bytes
    wav_file.setframerate(rate)    # sampling rate in Hz

    # write samples to the file
    wav_file.writeframes(input_audio)



def main():
  #print_all_devices()
  print("Width =", GetSystemMetrics(0))
  print("Height =", GetSystemMetrics(1))
  """
  dev_dict = explore_devices(name="MOTU Audio ASIO")
  device_idx = dev_dict["index"]
  record(device_index=device_idx, output_filename="./trial_out.wav", channels=4)"""


if __name__ == "__main__":
  #main()
  print_all_devices()
  #explore_devices("MME")
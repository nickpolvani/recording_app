# A dual task paradigm for voice-induced cognitive load

This repo contains the protocol and the software for the experiment conducted in June 2021 at BIC.

In this experiment, subjects were asked to read out loud sentences while listening to random syllables.
A dual task was induced as subjects had to count the number of syllables that occurred while speaking

## Installation
For now, the framework only works on Windows, with conda support.
Here are the steps to test it:
1. Create an empty directory
2. Download the <a href="https://www.unige.ch/lettres/linguistique/research/latl/siwis/database/">SIWIS</a> database (for Logitech: available on Google Drive), and unzip it in the new directory.
3. Download an excerpt from the <a href="https://doi.org/10.35111/qmyb-6884">Articulation index</a> (for Logitech: available on Google Drive), and unzip it in the new directory.
4. Download the source code with (i.e., by cloning the current repo)
The directory should look like this:
    ```bash
    Dir\
    ├── ...
    ├── articulation_index\         # Articulation index
    │   ├── ...
    │   └── data
    │        ├── ...
    │        └── syls
    │            ├── ...
    │            └── wb\
    │                 ├── s\        # Used syllables
    ├── siwis_database\             # SIWIS database
    ├── gui_v4.py                   # main script
    ├── utils.py                    # utility functions
    ├── xpGUI.yml                   # environment setup
    └── ...
    ```
5. Navigate to Dir\, and create the conda environment with:
```console
conda env create -f xpGUI.yml
```
6. Activate the environment with:
```console
conda activate xpGUI
```
7. Run the GUI with:
```console
python gui_v4.py
```

## Workflow
   1. Press **Start Recording** and begin reading the sentence out loud, while memorizing the number of syllables in the audio.
   2. Once you read  the sentence AND the audio is played, stop the recording with **Stop Recording**
   3. At the end of each step, you will be asked to report how many syllables you heard in total, for feedback.
   4. Regarding the audio, I chose to fill the void between the syllables with AWGN (at half the power than the previous syllable).
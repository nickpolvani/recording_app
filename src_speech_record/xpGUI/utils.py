import librosa
import numpy as np
import os
import re
import tkinter as tk

from nltk.tokenize import RegexpTokenizer

def _vad_merge(w, top_db=20):
    """Remove silence based on DB thresholding.
    w: numpy.ndarray
        Audio array of shape (N,)
    top_db: float
        Decibel threshold
    """
    intervals = librosa.effects.split(w, top_db=top_db)
    return np.concatenate([w[s:e] for s, e in intervals], axis=None)

def _min_max_scaling(x, a=-1, b=1):
    """Scale data in [a, b]"""
    return (b - a) * (x - np.min(x)) / np.ptp(x) + a

def _lower_and_tokenize(text):
    """Tokenize and lowercase of a text prompt."""
    tokenizer = RegexpTokenizer(r'\w+')
    text = re.sub(r'\d+', ' ', text).lower()  # Remove digits and lowercase text
    return text, tokenizer.tokenize(text)

def _find_records(language, min_words=10, max_words=15):
    """Find unique sentences for a certain language.

    Sentences have to be longer than min_words and shorter than max_words.

    Parameters:
    --------
    language: str
        Chosen language
    """
    assert language in ['EN', 'FR'], 'Language not available. Try "EN" for English, "FR" for French.'

    # List of unwanted text scripts (grammatical mistakes, or prompted laughs from the subjects)
    blacklist = {
        'EN': (
            'EN_A_18_135.txt',
            'EN_A_30_135.txt',
            'EN_A3_01_135.txt',
            'EN_A3_03_135.txt',
            'EN_A3_04_135.txt',
            'EN_A3_05_135.txt',
            'EN_A3_07_135.txt',
            'EN_B1_06_113.txt',
            'EN_B1_09_113.txt',
            'EN_B2_13_113.txt',
            'EN_B_24_113.txt',
            'EN_B_25_113.txt',
            'EN_B_29_113.txt',
            'EN_B3_10_113.txt',
            'EN_B_32_113.txt',
            'EN_C1_12_136.txt',
            'EN_C1_12_138.txt',
            'EN_C1_20_136.txt',
            'EN_C_31_136.txt',
            'EN_C_31_138.txt',
            'EN_C_22_136.txt',
            'EN_C_22_138.txt',
            'EN_C_26_136.txt',
            'EN_C_26_138.txt',
            'EN_C_36_136.txt',
            'EN_C_36_138.txt',
            'EN_C1_12_013.txt',
            'EN_B_24_324.txt',
            'EN_C1_12_013.txt',
            'EN_C1_12_313.txt',
            'EN_C1_20_013.txt',
            'EN_C1_20_313.txt',
            'EN_C_22_013.txt',
            'EN_C_22_313.txt',
            'EN_C_26_013.txt',
            'EN_C_26_313.txt',
            'EN_C_31_013.txt',
            'EN_C_31_313.txt',
            'EN_C_36_013.txt',
            'EN_C_36_313.txt',
            'EN_C1_12_198.txt',
            'EN_C1_20_198.txt',
            'EN_C_22_198.txt',
            'EN_C_26_198.txt',
            'EN_C_31_198.txt',
            'EN_C_36_198.txt',
            'EN_B1_06_308.txt',
            'EN_B1_09_308.txt',
            'EN_B2_13_307.txt',
            'EN_B3_10_308.txt',
            'EN_B_29_308.txt',
            'EN_B_25_308.txt',
            'EN_B_24_308.txt',
            'EN_B1_09_185.txt',
            'EN_B1_06_185.txt',
            'EN_B_32_185.txt',
            'EN_B3_10_185.txt',
            'EN_B_29_185.txt',
            'EN_B_24_185.txt',
            'EN_B_25_185.txt',
            'EN_B2_13_185.txt',
            'EN_B1_06_300.txt',
            'EN_B_32_300.txt',
            'EN_B3_10_300.txt',
            'EN_B_29_300.txt',
            'EN_B_25_300.txt',
            'EN_B_24_300.txt',
            'EN_B1_09_300.txt',
            'EN_B1_06_300.txt',
            'EN_B_32_300.txt',
            'EN_B3_10_300.txt',
            'EN_B_29_300.txt',
            'EN_C_22_113.txt',
            'EN_C_26_113.txt',
            'EN_C_31_113.txt',
            'EN_C_36_113.txt',
            'EN_C1_12_113.txt',
            'EN_C1_20_113.txt',
            'EN_C1_12_112.txt',
            'EN_C1_20_112.txt',
            'EN_C1_20_134.txt',
            'EN_C_22_134.txt',
            'EN_C_26_134.txt',
            'EN_C_31_134.txt',
            'EN_C1_12_134.txt',
            'EN_C1_20_134.txt',
            'EN_C_36_134.txt',
        ),
        'FR': (
            'FR_A1_08_103.txt',
            'FR_A1_08_106.txt',
            'FR_A1_14_103.txt',
            'FR_A1_14_106.txt',
            'FR_A1_17_103.txt',
            'FR_A1_17_106.txt',
            'FR_A1_19_103.txt',
            'FR_A1_19_106.txt',
            'FR_A_18_103.txt',
            'FR_A_18_106.txt',
            'FR_A2_01_103.txt',
            'FR_A2_01_106.txt',
            'FR_A2_03_103.txt',
            'FR_A2_03_106.txt',
            'FR_A2_04_103.txt',
            'FR_A2_04_106.txt',
            'FR_A2_05_103.txt',
            'FR_A2_05_106.txt',
            'FR_A_27_103.txt',
            'FR_A_27_106.txt',
            'FR_A_30_103.txt',
            'FR_A_30_106.txt',
            'FR_A_34_103.txt',
            'FR_A_34_106.txt',
            'FR_A1_08_120.txt',
            'FR_A1_08_122.txt',
            'FR_A1_14_120.txt',
            'FR_A1_14_122.txt',
            'FR_A1_17_120.txt',
            'FR_A1_17_122.txt',
            'FR_A1_19_120.txt',
            'FR_A1_19_122.txt',
            'FR_A_18_120.txt',
            'FR_A_18_122.txt',
            'FR_A2_01_120.txt',
            'FR_A2_01_122.txt',
            'FR_A2_03_120.txt',
            'FR_A2_03_122.txt',
            'FR_A2_04_120.txt',
            'FR_A2_04_122.txt',
            'FR_A2_05_120.txt',
            'FR_A2_05_122.txt',
            'FR_A_27_120.txt',
            'FR_A_27_122.txt',
            'FR_A_30_120.txt',
            'FR_A_30_122.txt',
            'FR_A_34_120.txt',
            'FR_A_34_122.txt',
            'FR_A1_14_116.txt',
            'FR_A1_17_116.txt',
            'FR_A1_19_116.txt',
            'FR_A_18_116.txt',
            'FR_A2_01_116.txt',
            'FR_A2_03_116.txt',
            'FR_A2_04_116.txt',
            'FR_A2_05_116.txt',
            'FR_A_27_116.txt',
            'FR_A_30_116.txt',
            'FR_A_34_116.txt',
            'FR_A1_08_116.txt'
        )
    }

    language_blacklist = blacklist[language]

    f = open(f'siwis_database/prompts/ALL_{language}_prompts.txt', 'rt', encoding='utf-8').read()
    all_prompts = f.split('\n')

    prompts = []
    texts = []

    for prompt in all_prompts:
        if prompt:
            fname, raw_text = prompt.split('\t')

            text, word_list = _lower_and_tokenize(raw_text)

            if (min_words < len(word_list) <= max_words) & (text not in texts) & (fname not in language_blacklist):
                lang, id1, id2, id3 = fname.split('_')
                folder_name = '_'.join([lang, id1, id2])
                prompts.append(f'siwis_database/txt/{lang}/{folder_name}/{fname}')
                texts.append(text)

                # Sanity check
                assert(os.path.exists(prompts[-1]))

    print(f'Found {len(prompts)} records with {min_words}-{max_words} words')
    # Sort the file names by default
    return sorted(prompts)

def _init_root():
    """Initialize and create the root window."""
    root = tk.Tk()
    root.tk.call('encoding', 'system', 'utf-8')
    root.title('Baseline')
    root.attributes('-fullscreen', True)
    return root

def _init_results_folder():
    """Initialize a new folder for the current user."""
    user_idx = 0

    while os.path.isdir(f'results/{user_idx}'):
        user_idx += 1

    os.makedirs(f'results/{user_idx}')

    print(f'User index: {user_idx}')

    return user_idx

def _input_language():
    """Ask the user for their preferred language."""
    while True:
        try:
            language = int(input('Select your preferred language (0: English, 1: French): '))
        except ValueError:
            continue
        else:
            if language in {0, 1}:
                break
            else:
                print('Wrong argument. Try again')
    return language

#!/bin/bash
# 1 argument: glob pattern for all files to convert (with '')
# Converted files with .wav at the end and LibriSpeech changed into LibriSpeech-wav in the path.
# Original path must contain 'LibriSpeech'
# Example: ./convert_flac2wav.sh 'LibriSpeech/dev-clean/*/*/*.flac"

a=($1)
n_files="${#a[@]}"

i=0
for src in $1;do
  echo -ne "${i}/${n_files}\r"
  out="${src/"LibriSpeech"/"LibriSpeech-wav"}"
  out="${out/".flac"/".wav"}"
  dir="$(dirname "$out")"
  mkdir -p $dir

  # Check if file does not already exist
  if [ ! -f "$out" ]; then
    ffmpeg -loglevel quiet -i $src $out
  fi
  ((i=i+1))
done

echo "${n_files}/${n_files}"
echo "Done"
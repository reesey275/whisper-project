# Input Directory# Input Directory



Place your audio and video files here for transcription.Place your audio and video files here for transcription.



## Supported Formats## Supported Formats

- MP3, MP4, WAV, M4A, FLAC, OGG, AAC, WMA, WEBM- MP3, MP4, WAV, M4A, FLAC, OGG, AAC, WMA, WEBM



## Usage Examples## Usage Examples



```bash```bash

# Add your files to this directory# Add your files to this directory

cp your_audio.mp4 input/cp your_audio.mp4 input/



# Then transcribe using any method# Then transcribe using any method

python transcribe.py input/your_audio.mp4python transcribe.py input/your_audio.mp4

python clean_transcribe.py input/your_audio.mp4python clean_transcribe.py input/your_audio.mp4

``````



## Security Note## Security Note

This directory is excluded from git commits via .gitignore to protect your personal files.This directory is excluded from git commits via .gitignore to protect your personal files.

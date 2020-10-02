"""
File:           sathualab_speech_to_text.py
Author:         Dibyaranjan Sathua
Created on:     25/09/20, 6:26 PM
"""
import os
import sys
import glob

from pydub import AudioSegment
from google.cloud import speech
import wave

import bucket
import google_config
import sathualab_translate


def mp3_to_wav(audio_file_name):
    """ Convert MP3 to WAV """
    if audio_file_name.split('.')[1] == 'mp3':
        print(f"Converting mp3 to wav format")
        sound = AudioSegment.from_mp3(audio_file_name)
        audio_wav_file_name = audio_file_name.split('.')[0] + '.wav'
        sound.export(audio_wav_file_name, format="wav")
        return audio_wav_file_name, True
    return audio_file_name, False


def stereo_to_mono(audio_file_name):
    sound = AudioSegment.from_wav(audio_file_name)
    sound = sound.set_channels(1)
    sound.export(audio_file_name, format="wav")


def frame_rate_channel(audio_file_name):
    with wave.open(audio_file_name, "rb") as wave_file:
        frame_rate = wave_file.getframerate()
        channels = wave_file.getnchannels()
        return frame_rate, channels


def write_transcript(filename, transcript):
    """ Writing transcript to local file """
    with open(filename, mode="w") as outfile:
        outfile.write(transcript)


def google_transcribe(audio_file_name):
    # mp3 flag indicates if the input file is in mp3 format and converted to wav format
    audio_wav_file_name, mp3_flag = mp3_to_wav(audio_file_name)
    frame_rate, channels = frame_rate_channel(audio_wav_file_name)
    if channels > 1:
        stereo_to_mono(audio_wav_file_name)

    audio_wav_basename = os.path.basename(audio_wav_file_name)
    destination_blob_name = f"{google_config.SPEECH_AUDIO_FILES}/{audio_wav_basename}"

    # Uploading audio file to cloud storage
    print(f"Uploading {audio_wav_file_name} to cloud storage")
    input_uri = bucket.upload_to_bucket(
        google_config.BUCKETNAME,
        audio_wav_file_name,
        destination_blob_name
    )

    print(f"Input URI: {input_uri}")
    transcript = ''

    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(uri=input_uri)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=frame_rate,
        language_code='en-US')

    # Detects speech in the audio file
    print(f"Speech to text using Google API in progress")
    operation = client.long_running_recognize(request={"config": config, "audio": audio})
    response = operation.result(timeout=10000)

    for result in response.results:
        transcript += result.alternatives[0].transcript

    # Deleting the temp wav audio file created
    if mp3_flag:
        os.remove(audio_wav_file_name)
    # Deleting input audio from cloud storage
    bucket.delete_blob(google_config.BUCKETNAME, destination_blob_name)
    return transcript


def sathualab_speech_to_text(audio_file, output_transcribe_dir, translate=False,
                             translate_output_dir=None, source_lang_code=None, target_lang_codes=None):
    """ Convert speech to text and optionally translate it to a different language """
    audio_file_basename = os.path.basename(audio_file)
    # Coverting speech to text
    print(f"Converting speech to text")
    transcript = google_transcribe(audio_file)
    transcript_filename = os.path.splitext(audio_file_basename)[0] + ".txt"
    transcript_filename = os.path.join(output_transcribe_dir, transcript_filename)
    print(f"Saving the transcript file to {transcript_filename}")
    write_transcript(transcript_filename, transcript)
    if translate:
        print("Translating the transcript")
        sathualab_translate.sathualab_translate(
            input_file=transcript_filename,
            output_dir=translate_output_dir,
            source_lang_code=source_lang_code,
            target_lang_codes=target_lang_codes
        )


def main():
    """ Main code for sppech to text """
    print("Run Option")
    print("1. Single audio file")
    print("2. Directory of audio files")
    print("0. Exit")
    choice = int(input("Enter your choice: "))
    if choice == 1:
        audio_file = input("Enter the path of audio file (mp3/wav format): ")
        all_audio_files = [audio_file]
    elif choice == 2:
        audio_files_dir = input("Enter the path of the directory containing audio files (mp3/wav format): ")
        all_audio_files = glob.glob(os.path.join(audio_files_dir, "*.mp3")) + \
                          glob.glob(os.path.join(audio_files_dir, "*.wav"))
    else:
        sys.exit(0)

    translate_output_dir = None
    source_lang_code = None
    target_lang_codes = None
    # Common inputs
    output_transcribe_dir = input("Enter directory path to store transcripts: ")
    translate = input("Do you want to translate [y/n]: ")
    translate = translate.lower() == "y"
    if translate:
        translate_output_dir = input("Enter directory path to store the translations: ")
        source_lang_code = input("Source language (hit enter to autodetect): ")
        if source_lang_code == "":
            source_lang_code = None
        target_lang_codes = input(
            "Target languages (multiple lang should be comma separated like de, fr): ")

    for audio_file in all_audio_files:
        print(f"Processing audio file: {audio_file}")
        sathualab_speech_to_text(
            audio_file=audio_file,
            output_transcribe_dir=output_transcribe_dir,
            translate=translate,
            translate_output_dir=translate_output_dir,
            source_lang_code=source_lang_code,
            target_lang_codes=target_lang_codes
        )


if __name__ == "__main__":
    main()

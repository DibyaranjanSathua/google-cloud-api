"""
File:           sathualab_text_to_speech.py
Author:         Dibyaranjan Sathua
Created on:     28/09/20, 10:09 PM
"""
import os
from google.cloud import texttospeech

import google_config


def sathualab_text_to_speech(text):
    """ Text to Speech """
    client = texttospeech.TextToSpeechClient()
    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    audio_data = b''
    print("Converting text to speech")
    for i in range(google_config.TTS_MAX_REQUEST_PER_MINUTE):
        end_index = min(google_config.TTS_TOTAL_CHARACTERS_PER_REQUEST, len(text))
        text_to_process = text[:end_index]
        text = text[end_index:]
        input_text = texttospeech.SynthesisInput(text=text_to_process)
        response = client.synthesize_speech(
            request={"input": input_text, "voice": voice, "audio_config": audio_config}
        )
        # The response's audio_content is binary.
        audio_data += response.audio_content
        if not text:
            break

    return audio_data


def main():
    """ Main Function """
    text_file = input("Enter the path of text file: ")
    output_dir = input("Enter output directory: ")
    with open(text_file, "r") as f:
        text = f.read()

    max_chars_allowed = google_config.TTS_MAX_REQUEST_PER_MINUTE * google_config.TTS_TOTAL_CHARACTERS_PER_REQUEST
    if len(text) > max_chars_allowed:
        print(f"Warning: Max {max_chars_allowed} characters allowed.")

    audio_data = sathualab_text_to_speech(text)
    output_file = os.path.join(output_dir, "audio_out.mp3")
    with open(output_file, mode="wb") as f:
        f.write(audio_data)

    print(f"Audio is downloaded to {output_file}")


if __name__ == "__main__":
    main()

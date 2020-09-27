"""
File:           google_config.py
Author:         Dibyaranjan Sathua
Created on:     27/09/20, 1:09 PM
"""
import os


BUCKETNAME = "sathuaaudiofiles"
TRANSLATE_INPUT_FILES = "translate_input"
TRANSLATE_OUTPUT_FILES = "translate_output"
SPEECH_AUDIO_FILES = "audio"
PROJECT_ID = "speech-api-290612"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = \
    "/home/dibyaranjan/Downloads/Speech API-06b76f1d45ce.json"

"""
File:           sathualab_translate.py
Author:         Dibyaranjan Sathua
Created on:     27/09/20, 11:51 AM
"""
import os
import sys
import glob
from google.cloud import translate

import bucket
import google_config


def get_supported_languages(project_id="YOUR_PROJECT_ID"):
    """Getting a list of supported language codes."""

    client = translate.TranslationServiceClient()

    parent = f"projects/{project_id}"

    # Supported language codes: https://cloud.google.com/translate/docs/languages
    response = client.get_supported_languages(parent=parent)

    # List language codes of supported languages.
    print("Supported Languages:")
    for language in response.languages:
        print("Language Code: {}".format(language.language_code))


def detect_language(project_id, content):
    """Detecting the language of a text string."""

    client = translate.TranslationServiceClient()

    location = "global"

    parent = f"projects/{project_id}/locations/{location}"

    # Detail on supported types can be found here:
    # https://cloud.google.com/translate/docs/supported-formats
    response = client.detect_language(
        content=content,
        parent=parent,
        mime_type="text/plain",  # mime types: text/plain, text/html
    )

    # Display list of detected languages sorted by detection confidence.
    # The most probable language is first.
    for language in response.languages:
        # The language detected
        print("Language code: {}".format(language.language_code))
        # Confidence of detection result for this language
        print("Confidence: {}".format(language.confidence))

    if response.languages:
        return response.languages.pop(0).language_code


def batch_translate_text(input_uri, output_uri, project_id, source_lang_code=None,
                         target_lang_codes=None, timeout=600):
    """Translates a batch of texts on GCS and stores the result in a GCS location."""
    if source_lang_code is None:
        source_lang_code = "en"

    if target_lang_codes is None:
        target_lang_codes = ["de"]

    client = translate.TranslationServiceClient()
    location = "us-central1"
    # Supported file types: https://cloud.google.com/translate/docs/supported-formats
    gcs_source = {"input_uri": input_uri}

    input_configs_element = {
        "gcs_source": gcs_source,
        "mime_type": "text/plain",  # Can be "text/plain" or "text/html".
    }
    gcs_destination = {"output_uri_prefix": output_uri}
    output_config = {"gcs_destination": gcs_destination}
    parent = f"projects/{project_id}/locations/{location}"

    # Supported language codes: https://cloud.google.com/translate/docs/language
    operation = client.batch_translate_text(
        request={
            "parent": parent,
            "source_language_code": source_lang_code,
            "target_language_codes": target_lang_codes,  # Up to 10 language codes here.
            "input_configs": [input_configs_element],
            "output_config": output_config,
        }
    )

    print("Waiting for operation to complete...")
    response = operation.result(timeout)

    print("Total Characters: {}".format(response.total_characters))
    print("Translated Characters: {}".format(response.translated_characters))


def sathualab_translate(input_file, output_dir, source_lang_code=None, target_lang_codes=None):
    """ Translate text file using google API """
    input_basename = os.path.basename(input_file)
    destination_blob_name = f"{google_config.TRANSLATE_INPUT_FILES}/{input_basename}"
    input_uri = bucket.upload_to_bucket(
        google_config.BUCKETNAME,
        input_file,
        destination_blob_name
    )
    output_uri = f"gs://{google_config.BUCKETNAME}/{google_config.TRANSLATE_OUTPUT_FILES}/"
    print(f"Input URI: {input_uri}")
    print(f"Output URI: {output_uri}")
    if source_lang_code is None:
        print(f"Detecting source language")
        # Detect the language automatically
        with open(input_file, mode="r") as infile:
            content = infile.read(50)
        source_lang_code = detect_language(google_config.PROJECT_ID, content)

    print(f"Source language: {source_lang_code}")

    if target_lang_codes is None:
        target_lang_codes = ["de"]
    else:
        target_lang_codes = [x.strip() for x in target_lang_codes.split(",")]

    print(f"Target languages: {target_lang_codes}")
    print(f"Translating using Google API in progress")
    batch_translate_text(
        input_uri,
        output_uri,
        google_config.PROJECT_ID,
        source_lang_code,
        target_lang_codes
    )

    # Delete input blob
    print(f"Delete input file from cloud storage: {destination_blob_name}")
    bucket.delete_blob(google_config.BUCKETNAME, destination_blob_name)

    # Download translated files
    print(f"Downloading translating files to {output_dir}")
    input_basename_without_ext = os.path.splitext(input_basename)[0]
    for lang in target_lang_codes:
        output_filename = f"{google_config.BUCKETNAME}_{google_config.TRANSLATE_INPUT_FILES}_" \
                          f"{input_basename_without_ext}_{lang}_translations.txt"
        blob_name = f"{google_config.TRANSLATE_OUTPUT_FILES}/{output_filename}"
        bucket.download_from_bucket(google_config.BUCKETNAME, blob_name, output_dir)
        print(f"Downloaded: {output_filename}")

    # Delete output translated directory
    bucket.delete_blob(google_config.BUCKETNAME, f"{google_config.TRANSLATE_OUTPUT_FILES}")


def main():
    """ Main function for translation """
    print("Run Option")
    print("1. Single text file")
    print("2. Directory of text files")
    print("0. Exit")
    choice = int(input("Enter your choice: "))
    if choice == 1:
        text_file = input("Enter the path of text file (with .txt extension): ")
        all_text_files = [text_file]
    elif choice == 2:
        text_files_dir = input(
            "Enter the path of the directory containing text files (with .txt extension): ")
        all_text_files = glob.glob(os.path.join(text_files_dir, "*.txt"))
    else:
        sys.exit(0)

    translate_output_dir = input("Enter directory path to store the translations: ")
    source_lang_code = input("Source language (hit enter to autodetect): ")
    if source_lang_code == "":
        source_lang_code = None
    target_lang_codes = input("Target languages (multiple lang should be comma separated like de, fr): ")

    for text_file in all_text_files:
        print(f"Processing file: {text_file}")
        sathualab_translate(
            input_file=text_file,
            output_dir=translate_output_dir,
            source_lang_code=source_lang_code,
            target_lang_codes=target_lang_codes
        )


if __name__ == "__main__":
    main()

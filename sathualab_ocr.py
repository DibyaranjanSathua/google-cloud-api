"""
File:           sathualab_ocr.py
Author:         Dibyaranjan Sathua
Created on:     29/09/20, 1:57 AM
"""
import io
import glob
import os
import sys
from google.cloud import vision

import google_config


def detect_text(path):
    """Detects text in the file."""

    client = vision.ImageAnnotatorClient()

    # [START vision_python_migration_text_detection]
    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    print("Detecting texts")
    response = client.text_detection(image=image)
    texts = response.text_annotations
    for text in texts:
        print('\n"{}"'.format(text.description))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    return texts.pop(0).description


def main():
    """ Main function """
    print("Run Option")
    print("1. Single image file")
    print("2. Directory of image files")
    print("0. Exit")
    choice = int(input("Enter your choice: "))
    if choice == 1:
        image_file = input("Enter the path of image file: ")
        all_image_files = [image_file]
    elif choice == 2:
        image_files_dir = input("Enter the path of the directory containing image files: ")
        all_image_files = glob.glob(os.path.join(image_files_dir, "*"))
    else:
        sys.exit(0)

    output_dir = input("Enter the path of output directory: ")
    for image_file in all_image_files:
        print(f"Processing image: {image_file}")
        basename = os.path.basename(image_file)
        filename = f"{os.path.splitext(basename)[0]}.txt"
        output_file = os.path.join(output_dir, filename)
        text = detect_text(image_file)
        with open(output_file, mode="w") as f:
            f.write(text)
        print(f"Saved detected text to {output_file}")


if __name__ == '__main__':
    main()

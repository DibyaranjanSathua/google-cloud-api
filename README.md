# google-cloud-api (SathuaLab)

1. Create a Project on Google Cloud
2. Enable Google Speech to Text and Google translate
3. Download the JSON authentication file (https://cloud.google.com/translate/docs/setup#auth) 
4. Create a bucket in Google storage
5. Edit google_config.py file
    a. Change BUCKETNAME to your bucket name on google cloud
    b. Change PROJECT_ID to your Google project ID
    c. Set GOOGLE_APPLICATION_CREDENTIALS to your JSON authentication file (Step 3)
   
6. Clone the repo using "git clone https://github.com/DibyaranjanSathua/google-cloud-api.git"
7. cd to the root directory of the cloned repo 
8. Create a virtual environment using "python3 -m venv venv"
9. Activate venv by "source venv/bin/activate"
10. Install all python dependencies by "pip3 install -r requirements.txt"
11. Run Speech to Text using "python3 sathualab_speech_to_text.py"
    a. This also has an option to translate the transcripts. But that is optional
    
12. If you want to run only translation, you can run using "python3 sathualab_translate.py"
13. Languages should be input as Google Codes (https://cloud.google.com/translate/docs/languages)
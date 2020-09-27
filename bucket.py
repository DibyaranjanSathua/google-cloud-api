"""
File:           bucket.py
Author:         Dibyaranjan Sathua
Created on:     27/09/20, 1:09 PM
"""
from google.cloud import storage


def upload_to_bucket(bucket_name, source_file_name, destination_blob_name):
    """ Uploads a file to the bucket """
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    gcs_uri = 'gs://' + bucket_name + '/' + destination_blob_name
    return gcs_uri


def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    # blob = bucket.blob(blob_name)
    # blob.delete()
    blobs = bucket.list_blobs(prefix=blob_name)
    for blob in blobs:
        blob.delete()


def download_from_bucket(bucket_name, blob_name, destination_directory):
    """ Save a file from bucket to local disk """
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob_basename = blob.name.split("/")[-1]
    destination_uri = f"{destination_directory}/{blob_basename}"
    blob.download_to_filename(destination_uri)


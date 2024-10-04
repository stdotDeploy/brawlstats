import os
from google.cloud import storage

class GCPBucket:
    def __init__(self, json_key_path):
        self.set_credentials(json_key_path)
        self.client = self.create_client()
        self.print_connection_message()  # Optional feedback

    def set_credentials(self, json_key_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_key_path

    def create_client(self):
        return storage.Client()  # Initialize and return the client

    def print_connection_message(self):
        print("Authenticated and connected to Google Cloud Storage")  # Optional feedback

    def upload_to_bucket(self, bucket_name, blob_name, file_path):
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        print(f"File {file_path} uploaded to {blob_name} in bucket {bucket_name}.")

    def download_from_bucket(self, bucket_name, blob_name, destination_file_name):
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.download_to_filename(destination_file_name)
        print(f"Blob {blob_name} downloaded to {destination_file_name} from bucket {bucket_name}.")

    def list_blobs_in_bucket(self, bucket_name):
        bucket = self.client.bucket(bucket_name)
        blobs = bucket.list_blobs()
        print(f"Files in bucket {bucket_name}:")
        for blob in blobs:
            print(blob.name)

    def delete_blob_from_bucket(self, bucket_name, blob_name):
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.delete()
        print(f"Blob {blob_name} deleted from bucket {bucket_name}.")



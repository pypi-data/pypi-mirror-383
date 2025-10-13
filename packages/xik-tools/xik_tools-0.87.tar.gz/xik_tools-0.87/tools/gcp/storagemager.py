import logging
from google.cloud import storage
from google.oauth2 import service_account
from datetime import timedelta

class StorageManager:
    def __init__(self, credentials_file=None):
        if credentials_file is not None:
            self.credentials = service_account.Credentials.from_service_account_file(credentials_file)
            logging.info("Credentials loaded successfully.")
            self.client = storage.Client(credentials=self.credentials)
        else:
            self.client = storage.Client()
        logging.info("Google Cloud Storage client initialized successfully.")

    def upload_file(self, bucket_name, file_path, destination_blob_name, make_public=False):
            bucket = self.client.get_bucket(bucket_name)
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_filename(file_path)
            
            if make_public:
                blob.make_public()
                logging.info(f"File {destination_blob_name} is now public: {blob.public_url}")
            
            logging.info(f"File {file_path} uploaded to {destination_blob_name}.")


    def download_file(self, bucket_name, blob_name, destination_file_path):
        bucket = self.client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.download_to_filename(destination_file_path)
        logging.info(f"File {blob_name} downloaded to {destination_file_path}.")

    
    def list_files_in_bucket(self, bucket_name):
        bucket = self.client.get_bucket(bucket_name)
        blobs = bucket.list_blobs()
        sorted_blobs = sorted(blobs, key=lambda blob: blob.time_created)
        return [blob.name for blob in sorted_blobs]
        
    

    def make_file_public(self, bucket_name, blob_name):
        bucket = self.client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.make_public()
        logging.info(f"File {blob_name} is publicly accessible at: {blob.public_url}")
        return blob.public_url
    
    def bucket_exists(self, bucket_name):
        try:
            self.client.get_bucket(bucket_name)
            logging.info(f"Bucket {bucket_name} exists.")
            return True
        except Exception as e:
            logging.error(f"Bucket {bucket_name} does not exist: {e}")
            return False

    def get_url_if_file_exists(self, bucket_name, file_name, signed_expiration_hours=1, use_public=False):
            """
            버킷에서 파일명이 존재하면 Public URL 또는 Signed URL을 반환하는 함수
            
            Args:
            bucket_name (str): 검색할 버킷 이름
            file_name (str): 검색할 파일 이름
            expiration_hours (int): Signed URL 유효 기간 (기본값은 1시간)
            use_signed (bool): True이면 Signed URL을 사용, False이면 Public URL을 사용
            
            Returns:
            str: 파일이 존재하면 Public URL 또는 Signed URL 반환, 없으면 None 반환
            """
            try:
                bucket = self.client.get_bucket(bucket_name)
                blobs = bucket.list_blobs()

                for blob in blobs:
                    if blob.name == file_name:
                        if use_public and blob.public_url:
                            # 공개 URL을 반환
                            logging.info(f"File {file_name} found. Public URL: {blob.public_url}")
                            return blob.public_url
                        
                        else:
                            # Signed URL 생성
                            url = blob.generate_signed_url(
                                version="v4",
                                expiration=timedelta(hours=signed_expiration_hours),  # URL 유효 기간 설정
                                method="GET"  )
                            logging.info(f"File {file_name} found. Signed URL: {url}")
                            return url
                
                logging.info(f"File {file_name} not found in bucket {bucket_name}.")
                return None
            except Exception as e:
                logging.error(f"Error while checking for file: {e}")
                return None
from google.cloud import storage
import pyarrow.parquet as pq
from google.oauth2 import service_account
import logging
import pandas as pd
import io
import pyarrow as pa

class ParquetHandler:
    def __init__(self, bucket_name, credentials_file=None):
        """
        :param credentials_file: 서비스 계정 키 파일 경로
        :param bucket_name: GCS 버킷 이름
        """
        if credentials_file:
            self.credentials = service_account.Credentials.from_service_account_file(credentials_file)
            self.storage_client = storage.Client(credentials=self.credentials)
            logging.info("서비스 계정 키를 이용해 인증되었습니다.")
        else:
            self.storage_client = storage.Client()  
            logging.info("환경 기본 인증(Default Credentials)으로 인증되었습니다.")
    
        self.bucket_name = bucket_name
        self.bucket = self.storage_client.bucket(bucket_name)

    def read_parquet_from_gcs(self, file_name, columns= list| None):
        """
        Cloud Storage에서 Parquet 파일을 읽어오는 메소드.

        :param file_name: GCS 파일 이름 (경로 포함)
        :param columns: 읽을 컬럼 목록 (선택적)
        :return: Pandas DataFrame
        """
        blob = self.bucket.blob(file_name)

        # GCS에서 파라큇 파일을 메모리로 다운로드
        parquet_data = blob.download_as_bytes()
        
        # 필요한 컬럼만 읽기
        table = pq.read_table(io.BytesIO(parquet_data), columns=columns)
        return table.to_pandas()

    def save_parquet_to_gcs(self, file_name, df):
        """
        Pandas DataFrame을 Parquet 파일로 변환하여 Cloud Storage에 저장하는 메소드.

        :param file_name: GCS 파일 이름 (경로 포함)
        :param df: 저장할 Pandas DataFrame
        """
        blob = self.bucket.blob(file_name)

        # Pandas DataFrame을 Parquet 포맷으로 변환하여 GCS에 저장
        table = pa.Table.from_pandas(df)
        with blob.open("wb") as f:
            pq.write_table(table, f)

    def upsert_parquet_to_gcs(self, file_name, new_df, key_columns=None):
        """
        GCS의 Parquet 파일을 읽고, 새로운 데이터를 추가하거나 병합(upsert)하여 저장하는 메소드.
        파일이 없으면 새로 생성합니다.

        :param file_name: GCS 파일 이름 (경로 포함)
        :param new_df: 추가하거나 병합할 Pandas DataFrame
        :param key_columns: 병합할 때 사용할 key 컬럼 리스트 (없으면 단순 append)
        """
        if key_columns is None:
           key_columns = list(new_df.columns)
        
        blob = self.bucket.blob(file_name)

        try:
            if blob.exists():  # 파일이 존재하면 읽기
                existing_df = self.read_parquet_from_gcs(file_name)
                if key_columns:
                    # 키 컬럼을 기준으로 중복 제거 (new_df 기준으로 업데이트)
                    combined_df = pd.concat([existing_df, new_df])
                    combined_df.drop_duplicates(subset=key_columns, keep='last', inplace=True)
                else:
                    # 키 컬럼이 없으면 그냥 추가
                    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                # 파일이 없으면 새로 생성
                combined_df = new_df

            # 저장
            self.save_parquet_to_gcs(file_name, combined_df)
            logging.info(f"Parquet file '{file_name}' updated successfully.")

        except Exception as e:
            logging.error(f"Error in upsert_parquet_to_gcs: {e}")
            raise

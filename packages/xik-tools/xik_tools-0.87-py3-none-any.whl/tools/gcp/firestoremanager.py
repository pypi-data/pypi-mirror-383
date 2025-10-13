from google.cloud import firestore
from google.oauth2 import service_account
import logging
import pandas as pd

class FirestoreManager:
    def __init__(self, credentials_file=None):
        if credentials_file is not None:
            self.credentials = service_account.Credentials.from_service_account_file(credentials_file)
            logging.info("Credentials loaded successfully.")
            self.db = firestore.Client(credentials=self.credentials)
        else:
            self.db = firestore.Client()
        logging.info("Firestore client initialized successfully.")
        
    def save_dataframe(self, dict_data: dict, collection_name=None):
        collection_doc = self.db.collection(collection_name) if collection_name else self.db.collection("default_collection")

        for data_name, dataframe in dict_data.items():
            # 데이터프레임을 컬렉션의 문서로 저장
            for index, row in dataframe.iterrows():
                doc_key = f'{data_name}_doc_{index}'  # 문서 키 생성
                doc_ref = collection_doc.document(doc_key)  # 컬렉션 문서 참조
                doc_ref.set(row.to_dict())  # 데이터 저장
                logging.debug(f"Document {doc_key} added successfully under {collection_name}.")
        
        logging.info(f"Data saved successfully under collection {collection_name if collection_name else 'default_collection'}.")


    def read_data(self, collection_name: str) -> pd.DataFrame:
        logging.info(f"Reading data from collection: {collection_name}.")
        docs = self.db.collection(collection_name).stream()
        data = []
        doc_ids = []  # 문서 키를 저장할 리스트
        
        for doc in docs:
            data.append(doc.to_dict())
            doc_ids.append(doc.id)  # 문서의 키 값을 doc_ids에 추가
            logging.debug(f"Document {doc.id} retrieved successfully from {collection_name}.")
        
        if data:
            df = pd.DataFrame(data, index=doc_ids)  # DataFrame의 인덱스로 doc_ids 사용
            logging.debug(f"Successfully converted {len(data)} documents to DataFrame.")
            return df
        else:
            logging.warning(f"No documents found in collection: {collection_name}.")
            return pd.DataFrame()




    def save_db(self, doc_key: str, data_dict: dict = None, collection_name: str = "sample_collection"):
        """
        Firestore에 데이터를 저장하는 함수.

        Args:
            doc_key (str): 문서의 고유 키.
            data_dict (dict): Firestore에 저장할 데이터. 기본값은 빈 딕셔너리.
            collection_name (str): Firestore 컬렉션 이름 (기본값: "sample_collection").
        """
        if data_dict is None:
            data_dict = {}

        logging.info(f"Saving document with key: {doc_key}")
        doc_ref = self.db.collection(collection_name).document(doc_key)
        logging.info(f"Document reference path: {doc_ref.path}")

        try:
            doc_ref.set(data_dict)
            logging.info("Document saved successfully.")
        except Exception as e:
            logging.error(f"Error saving document: {e}")
            
            
    def get_all_document_keys(self, collection_name: str = "sample_collection")->list:
        """
        Firestore에서 특정 컬렉션의 모든 문서 키를 추출하는 함수.

        Args:
            collection_name (str): 컬렉션 이름 (기본값: "sample_collection").
        
        Returns:
            list: 문서 키들의 리스트.
        """
        logging.info(f"Fetching all document keys from collection '{collection_name}'")
        try:
            docs = self.db.collection(collection_name).stream()
            doc_keys = [doc.id for doc in docs]  # 문서의 id (키)를 추출
            logging.info(f"Retrieved {len(doc_keys)} document keys successfully.")
            return doc_keys
        except Exception as e:
            logging.error(f"Error fetching document keys: {e}")
            return []   
            
    def is_doc_key_exist(self, doc_key: str, collection_name: str = "sample_collection") -> bool:
        """
        Firestore에서 doc_key가 중복되는지 확인하는 함수.

        Args:
            doc_key (str): 확인할 문서의 고유 키.
            collection_name (str): 확인할 컬렉션 이름 (기본값: "sample_collection").

        Returns:
            bool: 문서가 존재하면 True, 존재하지 않으면 False.
        """
        logging.info(f"Checking if document with key '{doc_key}' exists in collection '{collection_name}'")
        doc_ref = self.db.collection(collection_name).document(doc_key)

        try:
            doc = doc_ref.get()
            if doc.exists:
                logging.info(f"Document with key '{doc_key}' already exists.")
                return True
            else:
                logging.info(f"Document with key '{doc_key}' does not exist.")
                return False
        except Exception as e:
            logging.error(f"Error checking document existence: {e}")
            return False
        
        
    def delete_document(self, doc_key: str, collection_name: str = "sample_collection"):
        """
        Firestore에서 특정 문서를 삭제하는 함수.

        Args:
            doc_key (str): 삭제할 문서의 고유 키.
            collection_name (str): 컬렉션 이름 (기본값: "sample_collection").
        """
        logging.info(f"Attempting to delete document with key '{doc_key}' from collection '{collection_name}'")
        doc_ref = self.db.collection(collection_name).document(doc_key)

        try:
            doc_ref.delete()
            logging.info(f"Document with key '{doc_key}' deleted successfully.")
        except Exception as e:
            logging.error(f"Error deleting document: {e}")
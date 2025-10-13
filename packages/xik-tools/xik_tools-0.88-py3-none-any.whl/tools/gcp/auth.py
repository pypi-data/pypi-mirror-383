from googleapiclient.discovery import build
from google.oauth2 import service_account
import logging
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

class GCP_AUTH:
    @staticmethod
    def authenticate_with_json(json_path: str):
        logging.info("Authenticating Google Calendar service...")
        try:
            # JSON 파일을 통해 자격 증명 생성
            credentials = service_account.Credentials.from_service_account_file(json_path)
            service = build('calendar', 'v3', credentials=credentials)
            logging.info("Successfully authenticated Google Calendar service.")
            return service
        except Exception as e:
            logging.error(f"Authentication failed: {e}")
            raise ValueError(f"Authentication failed: {e}")
    

    def get_access_token(json_path: str, SCOPES = ['https://www.googleapis.com/auth/calendar']):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret.json', SCOPES)
                creds = flow.run_local_server(port=8080)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        print('Initial authentication complete and token.pickle saved.')
        return 'token.pickle'


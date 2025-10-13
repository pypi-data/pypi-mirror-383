import requests
import base64
import pandas as pd
import json

class GitMgt:
    
    def __init__(self):
        pass
    
    @staticmethod    
    def upload_json_to_github(content, git_token, git_repo, file_name='data'):
        
        if isinstance(content, pd.DataFrame):
            json_content = content.to_json(orient='records', lines=True)
        elif isinstance(content, dict):
            json_content = json.dumps(content)
        else:
            raise ValueError("content는 DataFrame, dict 이어야 합니다.")
        
        encoded_content = base64.b64encode(json_content.encode('utf-8')).decode('utf-8')
        
        url = f'https://api.github.com/repos/{git_repo}/contents/{file_name}.json'
        
        headers = {
            'Authorization': f'token {git_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        data = {
            'message': 'Upload JSON file',
            'content': encoded_content, 
        }

        response = requests.put(url, headers=headers, json=data)

        if response.status_code == 201:
            print('파일이 성공적으로 업로드되었습니다!')
        else:
            print('업로드 실패:', response.json())
            
    def get_github_folder_files(owner, repo, path, branch="main"):
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
        headers = {"Accept": "application/vnd.github.v3+json"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            files = response.json()
            # 각 파일에 접근할 수 있는 raw URL을 생성하여 반환
            return [f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file['path']}" for file in files if file['type'] == 'file']
        else:
            print(f"Error {response.status_code}: {response.json().get('message')}")
            return []
        
    
    @staticmethod 
    def get_github_files_as_dict(owner, repo, path=""):
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        
        response = requests.get(url)
        
        # 요청이 성공적인지 확인
        if response.status_code == 200:
            files = response.json()  # JSON 형식으로 응답
            file_dict = {}

            for file in files:
                file_dict[file['name']] = file.get('download_url', None)
            
            return file_dict
        else:
            print(f"Error: {response.status_code}")
            return {}


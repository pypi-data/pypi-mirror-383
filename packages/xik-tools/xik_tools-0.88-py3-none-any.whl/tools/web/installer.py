import subprocess
import os
import platform
import logging
import requests
import zipfile
import shutil
from pathlib import Path


class Installer:
    chrome_path = Path("chrome") 
    chromedriver_path = Path("chromedriver")
    @staticmethod
    def install_chrome_and_driver():
        current_os = platform.system()
        
        chrome_path = Path.cwd() / Installer.chrome_path
        driver_path = Path.cwd() / Installer.chromedriver_path
        
        # 드라이버 경로 존재 여부 확인
        need_install = not os.path.exists(driver_path) or not os.path.exists(chrome_path)
        if need_install:
            logging.info("Chrome 또는 ChromeDriver가 존재하지 않습니다. 설치를 시작합니다.")
        else:
            logging.info("Chrome 및 ChromeDriver가 이미 존재합니다.")
            
        if current_os == "Linux":
            chrome_path, driver_path = Installer._install_chrome_and_driver_linux(need_install=need_install)
        elif current_os == "Windows":
            chrome_path, driver_path = Installer._install_chrome_and_driver_win(need_install=need_install)
        else:
            logging.error("지원하지 않는 운영체제입니다.")
            chrome_path, driver_path = None, None

        return {"chrome_path": chrome_path, "driver_path": driver_path}

    @staticmethod
    def _install_chrome_and_driver_linux(need_install=False) -> dict:
        if need_install:
            logging.info("Linux용 Chrome 및 ChromeDriver 설치 중...")
            
            # 쉘 스크립트 내용
            shell_script_content = """
            #!/bin/bash
        
            # Download and setup Chrome
            wget https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.69/linux64/chrome-linux64.zip
            unzip chrome-linux64.zip
            rm chrome-linux64.zip
            mv chrome-linux64 chrome
            rm chrome-linux64
        
            # Download and setup ChromeDriver
            wget https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.69/linux64/chromedriver-linux64.zip
            unzip chromedriver-linux64.zip
            rm chromedriver-linux64.zip
            mv chromedriver-linux64 chromedriver
            rm chromedriver-linux64
        
            # Return Chrome installation path and ChromeDriver path
            echo $(pwd)/chrome
            echo $(pwd)/chromedriver
            """

            script_file_path = "set_chrome.sh"
            with open(script_file_path, "w") as script_file:
                script_file.write(shell_script_content)

            # 쉘 스크립트 실행
            result = subprocess.run(["bash", script_file_path], capture_output=True, text=True)

            # 쉘 스크립트 파일 삭제 (선택 사항)
            os.remove(script_file_path)

            if result.returncode == 0:
                logging.info("Linux에 Chrome 및 ChromeDriver 설치 완료.")
            else:
                logging.error(f"설치 중 오류 발생: {result.stderr}")
        
        chrome_path = Path.cwd() / Installer.chrome_path/ Path("chrome")
        driver_path = Path.cwd() / Installer.chromedriver_path/ Path("chromedriver")
        
        return chrome_path, driver_path
    @staticmethod
    def _install_chrome_and_driver_win(need_install=False) -> dict:
        def download_and_extract(url, zip_filename, folder_name):
            try:
                # 현재 디렉터리 경로
                current_dir = os.getcwd()
                zip_file_path = os.path.join(current_dir, zip_filename)
                extract_dir = os.path.join(current_dir, f"{folder_name}-temp")

                # URL에서 파일 다운로드
                logging.info(f"Downloading from {url}...")
                response = requests.get(url)
                response.raise_for_status()

                # 다운로드한 내용을 zip 파일로 저장
                with open(zip_file_path, 'wb') as file:
                    file.write(response.content)

                # 압축을 풀 디렉터리 만들기
                os.makedirs(extract_dir, exist_ok=True)

                # ZIP 파일 압축 해제
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)

                # 압축을 푼 폴더 이름 변경 및 이동
                extracted_subfolder = os.path.join(extract_dir, os.listdir(extract_dir)[0])
                new_dir = os.path.join(current_dir, folder_name)
                shutil.rmtree(new_dir, ignore_errors=True)  # 기존 폴더가 있으면 삭제
                shutil.move(extracted_subfolder, new_dir)

            except requests.exceptions.RequestException as e:
                logging.error(f"Error downloading the file: {e}")
            except zipfile.BadZipFile:
                logging.error(f"Failed to extract the ZIP file: {zip_file_path}")
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
            finally:
                # ZIP 파일 및 임시 폴더 삭제
                os.remove(zip_file_path) if os.path.exists(zip_file_path) else None
                shutil.rmtree(extract_dir, ignore_errors=True)

        if need_install:
            logging.info("Windows용 Chrome 및 ChromeDriver 설치 중...")
            chromedriver_url = 'https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.69/win64/chromedriver-win64.zip'
            chrome_url = 'https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.69/win64/chrome-win64.zip'

            download_and_extract(chromedriver_url, 'chromedriver-win64.zip', 'chromedriver')
            download_and_extract(chrome_url, 'chrome-win64.zip', 'chrome')

        chrome_path = Path.cwd() / Installer.chrome_path/ Path("chrome.exe")
        driver_path = Path.cwd() / Installer.chromedriver_path/ Path("chromedriver.exe")
        
        return chrome_path, driver_path
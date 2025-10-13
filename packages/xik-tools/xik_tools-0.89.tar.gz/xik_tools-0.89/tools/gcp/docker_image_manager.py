import subprocess

class DockerImageManager:
    def __init__(self, project_id, image_name, tag='latest'):
        self.project_id = project_id
        self.image_name = image_name
        self.tag = tag

    def build_image(self):
        """Docker 이미지를 빌드합니다."""
        subprocess.run(['docker', 'build', '-t', f'gcr.io/{self.project_id}/{self.image_name}:{self.tag}', '.'], check=True)

    def push_image(self):
        """Docker 이미지를 Google Container Registry에 푸시합니다."""
        subprocess.run(['docker', 'push', f'gcr.io/{self.project_id}/{self.image_name}:{self.tag}'], check=True)

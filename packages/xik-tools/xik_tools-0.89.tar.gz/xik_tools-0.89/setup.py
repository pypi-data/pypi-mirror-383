from setuptools import setup, find_packages

setup(
    name='xik_tools',
    version='0.89',
    author='xikest',
    description='tools for web',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        'pandas',
        'selenium','openpyxl'
    ],

    entry_points={
        'console_scripts': [
            'install_env_script = my_package.install_env:main',
        ],
    },

    url='https://github.com/xikest/tools',  # GitHub 프로젝트 페이지 링크
    project_urls={
        'Source': 'https://github.com/xikest/tools',  # GitHub 프로젝트 페이지 링크
        'Bug Tracker': 'https://github.com/xikest/tools',  # 버그 트래커 링크
    },
)

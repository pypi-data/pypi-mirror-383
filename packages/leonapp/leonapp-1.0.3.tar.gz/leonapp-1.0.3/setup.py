import os
from setuptools import setup, find_packages

def read_readme():
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    return ""

def read_requirements():
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r', encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

# 收集需要打包的根目录文件
root_files = []
exclude_dirs = ['__pycache__', 'dist', 'build', 'leonapp.egg-info', '__pycache__']
exclude_files = ['setup.py', 'requirements.txt']

for file in os.listdir('.'):
    file_path = os.path.join('.', file)
    if os.path.isfile(file_path) and file not in exclude_files:
        root_files.append(file_path)
    elif os.path.isdir(file_path) and file not in exclude_dirs:
        for root, _, files in os.walk(file_path):
            for f in files:
                root_files.append(os.path.join(root, f))

setup(
    name="leonapp",
    version="1.0.3",
    packages=find_packages(),
    author="JGZ_YES",
    author_email="luoriguodu@qq.com",
    description="LeonAPP应用程序启动器",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/JGZYES/leonapp",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'leonapp = leonapp.launcher:main',
        ],
    },
    package_data={
        'leonapp': ['*.py'],
    },
    # 配置根目录文件打包
    data_files=[('leonapp_data', root_files)],
)
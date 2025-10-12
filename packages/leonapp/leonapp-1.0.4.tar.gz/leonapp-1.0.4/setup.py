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

# 收集所有需要打包的文件
def get_all_files():
    # 需要排除的目录和文件
    exclude_dirs = {'__pycache__', 'dist', 'build', 'leonapp.egg-info', '.git'}
    exclude_files = {'setup.py', 'requirements.txt', '.gitignore'}
    
    all_files = []
    
    # 遍历当前目录下的所有文件和子目录
    for root, dirs, files in os.walk('.'):
        # 过滤掉要排除的目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            # 过滤掉要排除的文件
            if file in exclude_files:
                continue
                
            file_path = os.path.join(root, file)
            # 计算相对路径，去掉开头的"./"
            relative_path = os.path.relpath(file_path, '.')
            all_files.append(relative_path)
    
    return all_files

# 获取所有要打包的文件
package_files = get_all_files()

setup(
    name="leonapp",
    version="1.0.4",  # 重要：使用新的版本号
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
    # 配置数据文件打包
    data_files=[
        # 将所有收集的文件安装到leonapp_data目录
        ('leonapp_data', package_files)
    ],
    # 确保包数据被正确包含
    include_package_data=True,
)
    
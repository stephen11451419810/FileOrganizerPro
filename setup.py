#!/usr/bin/env python3
"""安装脚本"""

from setuptools import setup, find_packages

setup(
    name="FileOrganizerPro",
    version="1.0.0",
    author="Your Name",
    description="智能文件整理工具 - 支持发票识别和AI分类",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "colorama>=0.4.6",
        "tqdm>=4.66.1",
        "pypdf2>=3.0.1",
        "Pillow>=10.1.0",
    ],
    entry_points={
        "console_scripts": [
            "file-organizer=src.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.8",
)

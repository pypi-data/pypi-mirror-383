from setuptools import setup, find_packages

setup(
    name="oniondctw",
    version="1.1.1",
    author="2023_tw",
    author_email="skull@tw-yichen.net",
    description="洋蔥工具包 🧅 簡單、有趣、強大！",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dc2023tw/onion",
    packages=find_packages(),
    install_requires=[
        "requests",
        "discord.py",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",  
    ],
)

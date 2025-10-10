#!/usr/bin/env python3
"""
Setup script for XIBE-CHAT CLI
"""

from setuptools import setup, find_packages
import os

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="xibe-chat-cli",
    version="0.5.1",
    author="iotserver24",
    author_email="your-email@example.com",  # Replace with your email
    description="XIBE-CHAT CLI - AI-powered terminal assistant for text and image generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iotserver24/xibe-chat-cli",
    packages=find_packages(),
    py_modules=["xibe_chat"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Chat",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Graphics",
        "Topic :: System :: Shells",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "xibe-chat=xibe_chat:main",
            "xibe=xibe_chat:main",  # Short alias
        ],
    },
    keywords="ai, chat, cli, image-generation, text-generation, terminal, assistant",
    project_urls={
        "Bug Reports": "https://github.com/iotserver24/xibe-chat-cli/issues",
        "Source": "https://github.com/iotserver24/xibe-chat-cli",
        "Documentation": "https://github.com/iotserver24/xibe-chat-cli#readme",
    },
)

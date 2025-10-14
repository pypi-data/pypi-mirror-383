#!/usr/bin/env python3
"""
Setup script for Notifio - Universal Telegram notification service.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'NOTIFIO_README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Notifio - Universal Telegram notification service"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return ['requests>=2.25.0', 'python-dotenv>=0.19.0']

setup(
    name="notifio",
    version="1.0.0",
    author="Slav Fokin",
    author_email="support@innolope.com",
    description="Universal Telegram notification service for Python applications",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/innolope/notifio",  # Update with your repository URL
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "notifio-test=notifio.test_notifio:main",
        ],
    },
    keywords="telegram, notification, bot, messaging, alerts, monitoring",
    project_urls={
        "Bug Reports": "https://github.com/innolope/notifio/issues",
        "Source": "https://github.com/innolope/notifio",
        "Documentation": "https://github.com/innolope/notifio#readme",
    },
)

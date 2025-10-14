#!/usr/bin/env python3
"""
Setup script for isA Agent CLI
"""

from setuptools import setup, find_packages
import os

# Read requirements
def read_requirements():
    req_file = os.path.join(os.path.dirname(__file__), "requirements-cli.txt")
    if os.path.exists(req_file):
        with open(req_file, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return ["httpx>=0.25.0", "rich>=13.0.0", "requests>=2.25.0"]

# Read long description
def read_long_description():
    readme_file = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_file):
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "Command Line Interface for isA Agent API"

setup(
    name="isa-agent-cli",
    version="1.0.0",
    description="Command Line Interface for isA Agent API",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    author="isA Agent Team",
    author_email="support@isa-agent.com",
    url="https://github.com/isa-agent/cli",
    packages=find_packages(),
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'isa-chat=isa_cli.cli:cli',
            'isa-agent=isa_cli.cli:cli',
            'isachat=isa_cli.cli:cli',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="ai agent chat cli command-line api",
    python_requires=">=3.8",
    include_package_data=True,
    zip_safe=False,
)
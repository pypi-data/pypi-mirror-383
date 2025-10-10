from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dns-checker-cli",
    version="0.1.1",
    author="JINWOO",
    author_email="",
    description="A CLI tool for DNS lookups, SSL inspection, and HTTP pinging",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jinwoo-j/dns-checker",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "click>=8.0.0",
        "dnspython>=2.0.0",
        "cryptography>=3.4.0",
        "requests>=2.25.0",
        "rich>=10.0.0",
        "urllib3>=1.26.0",
    ],
    entry_points={
        "console_scripts": [
            "dns-checker=dns_checker.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="dns ssl certificate http ping monitoring cli",
)

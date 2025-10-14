# setup.py

from setuptools import setup, find_packages

# Read your README.md using UTF-8 to avoid UnicodeDecodeError
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="withopen",
    version="6.0.0",
    author="henry",
    author_email="osas2henry@gmail.com",
    description="A structured and backup-friendly way to manage `.txt` files with multi-console and debugging support.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.7",
    install_requires=[], 
)

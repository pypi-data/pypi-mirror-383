from setuptools import setup, find_packages

setup(
    name="emojitranslator",
    version="0.1.0",
    author="Eldar Eliyev",
    author_email="eldar2005matrix@gmail.com",
    description="Translate text to emojis",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/emojitranslator",
    packages=find_packages(),
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
)

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="audio-converter-pro",
    version="2.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Professional audio converter supporting multiple formats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/audio-converter-pro",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "customtkinter>=5.2.2",
        "pillow>=10.2.0",
        "mutagen>=1.47.0",
    ],
    entry_points={
        "console_scripts": [
            "audio-converter-pro=src.audio_converter_pro:main",
        ],
    },
    include_package_data=True,
)
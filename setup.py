from setuptools import setup, find_packages

setup(
    name="prosodicprominence",
    version="0.1.0",
    author="Arun Singh",
    description="A toolkit for extracting word-level prosodic prominence from speech using pitch, energy, and event-based features.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "torch",
        "torchaudio",
        "praat-parselmouth",
        "textgrid",
        "numpy",
        "scipy"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
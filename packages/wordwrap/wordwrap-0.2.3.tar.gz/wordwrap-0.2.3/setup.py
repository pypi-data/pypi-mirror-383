from setuptools import setup, find_packages

setup(
    name="wordwrap",
    version="0.2.3",
    description="A simple library for wrapping text to a fixed column width.",
    author="pigmonchu",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
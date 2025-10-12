from setuptools import setup, find_packages

setup(
    name="wordwrap",
    version="0.1.0",
    description="A simple library for wrapping text to a fixed column width.",
    author="pigmonchu",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
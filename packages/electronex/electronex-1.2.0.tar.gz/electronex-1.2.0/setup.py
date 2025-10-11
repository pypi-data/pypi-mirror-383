from setuptools import setup, find_packages

setup(
    name="electronex",
    version="1.2.0",
    author="Hrishabh",
    author_email="hrishabhtest@gmail.com",
    description="Python package for ECE & CSE engineering utilities",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/hrishabhxcode/enginex",
    packages=find_packages(),
    python_requires=">=3.7, <4",
    install_requires=[
        "numpy",
        "matplotlib"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

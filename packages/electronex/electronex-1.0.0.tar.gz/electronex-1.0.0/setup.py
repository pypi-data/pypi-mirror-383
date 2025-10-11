from setuptools import setup, find_packages

setup(
    name="electronex",                # Package name on PyPI
    version="1.0.0",
    author="Hrishabh",
    author_email="hrishabhtest@gmail.com",
    description="Python package for ECE & CSE engineering utilities",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/hrishabhxcode/enginex",
    packages=find_packages(),          # Finds electronex folder automatically
    install_requires=[
        "numpy",
        "matplotlib"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)

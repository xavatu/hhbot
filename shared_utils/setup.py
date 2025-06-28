from setuptools import setup
from setuptools.config.expand import find_packages

setup(
    name="shared_utils",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "aiohttp==3.12.13",
        "fastapi==0.115.13",
        "setuptools==80.9.0",
    ],
)

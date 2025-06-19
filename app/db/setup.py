from setuptools import setup, find_packages

setup(
    name="db",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "SQLAlchemy==2.0.41",
        "setuptools==80.9.0",
    ],
)

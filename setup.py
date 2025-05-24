from setuptools import setup, find_packages

setup(
    name="nychaguard",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "flask",
        "python-dotenv",
        "pandas",
        "smolagents",
    ],
) 
from setuptools import setup, find_packages

setup(
    name="data-lib_save",
    version="0.1.1",
    description="A library for storing, processing, and transmitting data (JSON, HTTP).",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Unknow",
    packages=find_packages(),
    python_requires=">=3.7",
)
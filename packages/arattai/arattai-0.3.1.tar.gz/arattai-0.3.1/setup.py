from setuptools import setup, find_packages

setup(
    name="arattai",  # must be unique on PyPI
    version="0.3.1",
    author="Vivek Kumar",
    description="Python library for Arattai messaging API.",
    packages=find_packages(),
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown", 
)

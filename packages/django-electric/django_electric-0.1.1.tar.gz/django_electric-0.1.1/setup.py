"""
Django Electric - Django integration for Electric SQL
"""
from setuptools import setup

# Read the long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    long_description=long_description,
    long_description_content_type="text/markdown",
)

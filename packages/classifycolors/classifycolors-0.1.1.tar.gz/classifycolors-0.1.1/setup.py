from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="classifycolors",
    version="0.1.1",
    author="Elie Fares",
    packages=find_packages(),
    install_requires=[
    ],
    long_description=long_description,
    long_description_content_type="text/markdown"
)
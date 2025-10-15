from setuptools import setup, find_packages

with open("readme.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="AFL_2_MATH",
    version="4.0",
    packages=find_packages(),
    install_requires=[
        
    ],

    long_description=long_description,
    long_description_content_type="text/markdown",
)
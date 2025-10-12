from setuptools import setup, find_packages

setup(
    name="webscraper-lite",
    version="0.1.0",
    author="Jay Telgote",
    author_email="ijaytelgote@gmail.com",
    description="A simple Python web scraping utility",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/webscraper-lite",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4"
    ],
    python_requires=">=3.7",
)

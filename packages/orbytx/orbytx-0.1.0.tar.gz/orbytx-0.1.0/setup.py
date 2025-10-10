from setuptools import setup, find_packages

setup(
    name="orbytx",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer>=0.12.3",
        "rich>=13.7.1",
        "google-api-python-client>=2.114.0",
        "google-auth-oauthlib>=1.2.0",
        "google-auth-httplib2>=0.2.0",
    ],
    entry_points={
        "console_scripts": [
            "orbyt=orbyt.cli:main",
        ],
    },
)


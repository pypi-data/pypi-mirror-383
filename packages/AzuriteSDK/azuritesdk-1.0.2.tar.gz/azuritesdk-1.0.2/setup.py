from setuptools import setup, find_packages

setup(
    name="AzuriteSDK",
    version="1.0.2",
    author="kenftr",
    description="SDK for Azurite Discord Modular Bot",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "discord.py>=2.6.4",
        "pyyaml>=6.0.3"
    ],
)

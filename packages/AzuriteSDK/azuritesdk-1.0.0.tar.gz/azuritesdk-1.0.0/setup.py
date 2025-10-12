from setuptools import setup, find_packages

setup(
    name="azuritesdk",
    version="1.0.0",
    author="kenftr",
    description="SDK for Azurite Discord Modular Bot",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "discord.py>=2.6.4",
        "pyyaml>=6.0.3"
    ],
)

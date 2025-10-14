"""Setup script for erc8004-sdk package."""
from setuptools import setup, find_packages

setup(
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "erc8004": ["abis/*.json"],
    },
)

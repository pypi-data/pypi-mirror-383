from setuptools import setup, find_packages

setup(
    name="pyrbd3",
    version="1.0.0",
    packages=find_packages(include=["src/pyrbd3", "src/pyrbd3.*"]),
    install_requires=[
        "pandas",
        "networkx",
        "tqdm",
        "loguru"
    ],
)
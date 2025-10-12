from setuptools import find_packages, setup

VERSION = "5.2"
setup(
    name="moduvent",
    version=VERSION,
    description="A lightweight, modular event system for Python applications with plugin architecture support.",
    packages=find_packages(),
)

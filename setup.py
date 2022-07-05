# pip install .
from setuptools import setup

setup(
    name="thetadata",
    packages=["thetadata"],
    include_package_data=True,
    install_requires=["pydantic"],
)

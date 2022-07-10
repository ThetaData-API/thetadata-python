# pip install .
from setuptools import setup

setup(
    name="thetadata",
    version=1.0,
    packages=["thetadata"],
    include_package_data=True,
    install_requires=["pandas", "tqdm"],
)

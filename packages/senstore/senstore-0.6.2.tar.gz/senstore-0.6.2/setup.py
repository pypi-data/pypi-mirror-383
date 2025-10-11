from setuptools import setup  # type: ignore
import setuptools  # pyright: ignore[reportMissingModuleSource]

import senstore

with open("senstore/requirements.txt") as f:
    required = f.read().splitlines()
with open("README.md", "r") as f:
    long_description = f.read()

version = senstore.get_version()
setup(
    name="senstore",
    version=version,
    description="Minimalistic vectorized sentence store",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ptarau/senstore.git",
    author="Paul Tarau",
    author_email="ptarau@gmail.com",
    license="MIT",
    packages=setuptools.find_packages(),
    package_data={"senstore": ["*.txt"]},
    include_package_data=True,
    install_requires=required,
    zip_safe=False,
)

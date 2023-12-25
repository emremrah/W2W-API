from setuptools import find_packages, setup

from wtw import __version__

with open('requirements.txt', 'r') as f:
    required = f.read().splitlines()

setup(
    name="WhatToWatch",
    author="Emre Emrah",
    author_email="emremrah.ee@gmail.com",
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    description="WhatToWatch is a web application that helps you find movies to watch.",
    install_requires=required,
    python_requires='>=3.8',
)

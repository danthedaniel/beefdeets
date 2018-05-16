from setuptools import setup
from beefdeets import __version__


setup(
    name="beefdeets",
    version=__version__,
    packages=["beefdeets"],
    include_package_data=True,
    install_requires=[
        "flask==0.12.2",
        "mutagen==1.40.0"
    ]
)

from setuptools import setup
from beefdeets import __version__


setup(
    name="beefdeets",
    version=__version__,
    packages=["beefdeets"],
    include_package_data=True,
    install_requires=[
        "flask==1.0.2",
        "mutagen==1.40.0"
    ],
    python_requires='>3.6'
)

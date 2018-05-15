from setuptools import setup

setup(
    name="beefdeets",
    version="0.1.0",
    packages=["beefdeets"],
    include_package_data=True,
    install_requires=[
        "flask==0.12.2",
        "mutagen==1.40.0"
    ]
)

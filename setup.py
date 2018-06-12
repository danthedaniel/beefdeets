from setuptools import setup
from typing import List

from beefdeets.version import __version__


def remove_empty(paths: List[str]) -> List[str]:
    """Remove empty string from a list."""
    return [x for x in paths if len(x) > 0]


setup(
    name="beefdeets",
    version=__version__,
    packages=["beefdeets"],
    license="MIT",
    author="teaearlgraycold",
    url="https://github.com/teaearlgraycold/beefdeets",
    include_package_data=True,
    install_requires=remove_empty(open("requirements.txt").read().split("\n")),
    python_requires=">=3.6",
    test_suite="beefdeets.test",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Topic :: Multimedia",
        "Topic :: Utilities"
    ],
    entry_points={
        "console_scripts": [
            "beefdeets = beefdeets.__main__:main"
        ]
    }
)

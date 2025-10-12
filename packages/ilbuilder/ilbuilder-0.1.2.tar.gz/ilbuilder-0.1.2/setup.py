from setuptools import setup, find_packages
from ilbuilder.version import __version__

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setup(
    name='ilbuilder',
    version=__version__,
    packages=find_packages(),
    requires=[
        'colorama',
        'rushlib',
        'rushdata',
        'rushrunning'
        'pyinstaller'
    ],
    description='python builder',
    author='ndrzy',
    author_email='dandan0019@outlook.com',
    python_requires='>=3.10',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/meatdumplings0019/rushlib",

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
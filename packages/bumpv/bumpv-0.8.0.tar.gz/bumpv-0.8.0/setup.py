import re
from pathlib import Path
from setuptools import setup, find_packages

description = 'Version-bump your software with a single command!'
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='bumpv',
    version='0.8.0',
    url='https://github.com/kylieCat/bumpv',
    author='Kylie Auld',
    author_email='kylie.a@protonmail.com',
    license='MIT',
    packages=find_packages(),
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        "Click>=8.0.0",
        "pyaml==19.4.1",
    ],
    entry_points={
        'console_scripts': [
            'bumpv = bumpv:bumpv',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)

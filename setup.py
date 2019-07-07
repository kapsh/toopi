# pylint: disable=missing-docstring
import io
import os
import re

from setuptools import find_packages
from setuptools import setup


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u"")
    with io.open(filename, mode="r", encoding='utf-8') as file:
        return re.sub(text_type(r':[a-z]+:`~?(.*?)`'), text_type(r'``\1``'), file.read())


setup(
    name='toopi',
    version='0.1',
    url="https://github.com/borntyping/cookiecutter-pypackage-minimal",
    license='MIT',

    author='Alexander Kapshuna',
    author_email='kapsh@kap.sh',

    description='client for pastebins inspired by wgetpaste',
    long_description=read('README.rst'),

    packages=find_packages(exclude=('tests',)),

    install_requires=[
        'requests',
    ],

    extra_requires={
        'clip': ['pyperclip'],
    },

    entry_points={
        'console_scripts': [
            'toopi = toopi.cli:main',
        ]
    },

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
    ],
)

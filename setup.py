#!/usr/bin/env python
# coding=utf-8

from setuptools import setup


# Use semantic versioning: MAJOR.MINOR.PATCH
version = '0.1.0'


def get_requires():
    with open('requirements.txt', 'r') as f:
        requires = [i for i in map(lambda x: x.strip(), f.readlines()) if i]
    return requires


def get_long_description():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    # license='License :: OSI Approved :: MIT License',
    name='apitools',
    version=version,
    author='reorx',
    author_email='novoreorx@gmail.com',
    description='Building blocks for HTTP API development',
    url='https://github.com/reorx/apitools',
    long_description=get_long_description(),
    packages=[
        'apitools',
    ],
    # Or use (make sure find_packages is imported from setuptools):
    # packages=find_packages()
    install_requires=get_requires(),
    # package_data={}
    # entry_points={'console_scripts': ['foo = package.module:main_func']}
)

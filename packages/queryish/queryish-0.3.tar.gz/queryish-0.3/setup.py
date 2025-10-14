#!/usr/bin/env python

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name='queryish',
    version='0.3',
    description="A library for constructing queries on arbitrary data sources following Django's QuerySet API",
    author='Matthew Westcott',
    author_email='matthew.westcott@torchbox.com',
    url='https://github.com/wagtail/queryish',
    packages=["queryish"],
    include_package_data=True,
    license='BSD-3-Clause',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.28,<3.0",
    ],
    extras_require={
        "testing": [
            "responses>=0.23,<1.0",
            "django>=4.2",
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Framework :: Django',
    ],
)

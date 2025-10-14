#!/usr/bin/env python
"""
Setup configuration for salestrack Django app
"""
from setuptools import setup, find_packages
import os

# Read README file
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-salestrack',
    version='1.0.1',
    description='A Django app for tracking sales personnel, distributors, and retailers with Google Maps integration',
    long_description=read('README.md') if os.path.exists('README.md') else 'A Django app for tracking sales personnel, distributors, and retailers with Google Maps integration',
    long_description_content_type='text/markdown',
    author='Parijat Srivastava',
    author_email='parijat.shrivastava@sortstring.com',
    url='https://github.com/sortstring/django-salestrack',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    # Dependencies
    install_requires=[
        'Django>=3.2',
        'requests>=2.20.0',
        'python-dateutil>=2.7.0',
    ],

    # Optional dependencies
    extras_require={
        'mysql': [
            'mysqlclient>=2.0.0',
            'django-mysql>=4.5.0',
        ],
        'api': [
            'djangorestframework>=3.13.0',
        ],
        'dev': [
            'pytest>=6.0',
            'pytest-django>=4.0',
            'coverage>=5.0',
        ],
    },

    # Python version requirement
    python_requires='>=3.8',

    # Classifiers for PyPI
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],

    # Keywords for search
    keywords='django, sales, tracking, maps, google-maps, distributor, retailer',

    # License
    license='MIT',
)
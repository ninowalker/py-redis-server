import os
from setuptools import setup, find_packages

from rediserver import __version__

setup(
    name = "py-redis-server",
    version = __version__,
    author = "Nino Walker",
    author_email = "nino.walker@gmail.com",
    description = ("A simple async TCP server that speaks the Redis Protocol."),
    url="https://github.com/ninowalker/py-redis-server",
    license = "BSD",
    packages=['rediserver'],
    long_description=open('README.md').read(),
    install_requires=['redis>=2.4.1'],
    setup_requires=['nose>=1.0', 'coverage', 'nosexcover'],
    test_suite = 'nose.collector',
    classifiers=[
        "License :: OSI Approved :: BSD License",
    ],
    entry_points={
                  'console_scripts': ['pyyacc.validate = pyyacc.scripts.compile:validate_main',
                                      'pyyacc.sources = pyyacc.scripts.compile:sources_main',],
                  'zc.buildout': ['parse = pyyacc.buildout:ParseYAML']
    }
)

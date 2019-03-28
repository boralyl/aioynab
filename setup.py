import os
from setuptools import setup


# Use exec so pip can get the version before installing the module
version_filename = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'aioynab', '_version.py'))
with open(version_filename, 'r') as vf:
    exec(compile(vf.read(), version_filename, 'exec'), globals(), locals())

readme_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'README.rst'))
with open(readme_path, 'r') as fp:
    long_description = fp.read()

setup(
    name='aioynab',
    version=__version__,  # noqa -- flake8 should ignore this line
    description=('This module provides a YNAB API client implemented using '
                 'python 3 asyncio.'),
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/boralyl/aioynab',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords=['python', 'ynab', 'asyncio'],
    author='Aaron Godfrey',
    packages=[
        'aioynab',
    ],
    install_requires=[
        'aiohttp >= 3.0.0, < 4.0.0',
        'uvloop >= 0.12.0, < 0.13.0',
    ],
    extras_require={
        'docs': [
            'sphinx >= 1.5.4, < 2.0.0',
            'sphinx-autodoc-typehints >= 1.2.4, < 2.0.0',
            'sphinx-rtd-theme >= 0.2.4, < 1.0.0',
            'sphinxcontrib-httpdomain >= 1.5.0, < 2.0.0',
        ],
        'tests': [
            'aioresponses',
            'codecov',
            'coverage >= 4.4.1, < 5.0.0',
            'flake8 >= 3.3.0, < 4.0.0',
            'pytest >= 4.0.0, < 5.0.0',
        ],
    },
)

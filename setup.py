import os
from setuptools import setup


# Use exec so pip can get the version before installing the module
version_filename = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'aioynab', '_version.py'))
with open(version_filename, 'r') as vf:
    exec(compile(vf.read(), version_filename, 'exec'), globals(), locals())

readme_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'README.md'))
with open(readme_path, 'r') as fp:
    long_description = fp.read()

setup(
    name='aioynab',
    version=__version__,  # noqa -- flake8 should ignore this line
    description=('This module provides a YNAB API client implemented using '
                 'python 3 asyncio.'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/boralyl/aioynab',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
    keywords=['python', 'ynab', 'asyncio'],
    author='Aaron Godfrey',
    packages=[
        'aioynab',
    ],
    install_requires=[
        'aiohttp >= 3.5.0, < 4.0.0'
    ],
    extras_require={
        'docs': [
            'sphinx >= 1.5.4, < 2.0.0',
            'sphinx-autodoc-typehints >= 1.2.4, < 2.0.0',
            'sphinx-rtd-theme >= 0.2.4, < 1.0.0',
            'sphinxcontrib-httpdomain >= 1.5.0, < 2.0.0',
        ],
        'tests': [
            'coverage >= 4.4.1, < 5.0.0',
            'flake8 >= 3.3.0, < 4.0.0',
            'pytest >= 3.3.2, < 4.0.0',
        ],
    },
)

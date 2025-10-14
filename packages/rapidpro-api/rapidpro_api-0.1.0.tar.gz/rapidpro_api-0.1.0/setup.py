from setuptools import setup, find_packages

import os
import re

def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'rapidpro_api','version.py')
    with open(version_file, mode='r', encoding='utf-8') as f:
        version_line = next((line.strip() for line in f if "__version__" in line), None)
        if not version_line:
            raise RuntimeError("Unable to find version string.")
        version_match = re.match(r"^__version__ = ['\"]([^'\"]*)['\"]", version_line)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")


setup(
    name='rapidpro-api',
    version=get_version(),
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
        'rapidpro-python==2.17.0',
        'python-slugify==8.0.4',
        'requests==2.32.3',
        'pandas==2.2.3',
        'polars==1.30.0',
        'fsspec==2025.3.2',
        'pyarrow==18.1.0',
        'adlfs==2024.12.0',
        'deltalake==0.25.5',

    ],
    # development dependencies
    extras_require={
        'dev': [
            'pytest==8.3.5',
            'pytest-cov==6.1.1',
            'pytest-mock==3.15.1',
            'flake8==7.3.0',
            'black==25.9.0',
            'isort==7.0.0',
            'mypy==1.18.2',
            'sphinx==8.2.3',
            'sphinx_rtd_theme==3.0.2',
            'requests-mock==1.12.1',
            'freezegun==1.5.1'
        ]
    },
    author='merlos',
    author_email='merlos@users.github.com',
    description='A library for extracting and transforming data from RapidPro',
    keywords='rapidpro, data extraction, data transformation, rapidpro-api',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/unicef/magasin-primero-paquet',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
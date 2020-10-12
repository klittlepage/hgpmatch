# pylint: disable=missing-module-docstring

import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='hgpmatch',
    author='Kelly Littlepage',
    author_email='kelly@klittlepage.com',
    description='A CSV driven solver for the resident/hospital style '
                'matching markets',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/klittlepage/hgpmatch',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'matching>=1.3.2,<2',
        'fuzzywuzzy>=0.18.0,<0.19.0',
        'python-Levenshtein>=0.12.0,<1.0.0'
    ],
    extras_require={
        'dev': [
            'sphinx',
            'sphinx_rtd_theme',
            'pylint',
            'mypy',
            'autopep8',
            'coveralls',
            'pytest',
            'wheel'
        ]
    },
    scripts=['bin/hgpmatch']
)

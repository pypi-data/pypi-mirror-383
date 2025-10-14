import io
import re
from os.path import dirname
from os.path import join

from setuptools import setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


required_libs = [
    'degenerate-dna==0.1.2',
    'seqrecord-expanded==0.2.16',
]

setup(
    name='dataset-creator',
    version='0.7.0',
    license='BSD-3-clause',
    description='Takes SeqRecordExpanded objects and creates datasets for phylogenetic software',
    long_description='%s\n%s' % (read('README.rst'), re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))),
    author='Carlos Peña',
    author_email='mycalesis@gmail.com',
    url='https://github.com/carlosp420/dataset-creator',
    packages=['dataset_creator'],
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Utilities',
    ],
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    install_requires=required_libs,
    extras_require={
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
    },
    entry_points={
        'console_scripts': [
            'dataset_creator = dataset_creator.__main__:main',
        ]
    },
)

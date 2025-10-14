import io
import setuptools
from os.path import join
from os.path import dirname


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


setuptools.setup(
    name="seqrecord_expanded",
    version="0.2.15",
    license="BSD",
    url="https://github.com/carlosp420/seqrecord-expanded",

    author="Carlos Peña",
    author_email="mycalesis@gmail.com",

    description="Another SeqRecord class with methods: degenerate seqs, codon positions based on reading frames, etc.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',  # Add this line

    packages=['seqrecord_expanded'],

    install_requires=[
        'biopython==1.85',
        'degenerate-dna==0.1.2',
    ],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
)

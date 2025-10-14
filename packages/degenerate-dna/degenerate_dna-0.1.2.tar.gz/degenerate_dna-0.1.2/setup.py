import setuptools

setuptools.setup(
    name="degenerate-dna",
    version="0.1.2",
    url="https://github.com/carlosp420/degenerate-dna",

    author="Carlos Pena",
    author_email="mycalesis@gmail.com",

    description="Python implementation of the Degen Perl package by Zwick et al.",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[],

    license='BSD-3-Clause',
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)

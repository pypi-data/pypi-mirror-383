from setuptools import setup, find_packages
import sys

# Determine extra dependencies for specific Python versions
extras = []
if sys.version_info < (3, 8):
    extras.append('typing_extensions')
    
with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='AnsiLib',
    version='1.1.0',
    author='Bora Boyacıoğlu',
    author_email='boyacioglu20@itu.edu.tr',
    description='A library for handling ANSI codes',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/boraboyacioglu-itu/ansilib',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    license='MIT License',
    python_requires='>=3.5',
    install_requires=extras,
)
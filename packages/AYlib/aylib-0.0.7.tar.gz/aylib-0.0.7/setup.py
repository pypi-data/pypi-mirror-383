from setuptools import setup, find_packages
import os

# Read the README file for long description
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='AYlib',
    version='0.0.7',
    description='A comprehensive Python utility library for network communication, serial communication, database operations, and data visualization',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='GNU3.0 License',
    url='https://github.com/AaronYang233/AYlib',
    author='Aaron Yang',
    author_email='3300390005@qq.com',
    packages=['AYlib'],
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.7',
    install_requires=[
        'pyserial>=3.0',
        'requests>=2.20.0',
        'matplotlib>=3.0.0',
        'numpy>=1.15.0',
        'PyMySQL>=0.9.0',
        'crcmod>=1.7',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=['socket', 'serial', 'database', 'ui', 'utilities'],
)
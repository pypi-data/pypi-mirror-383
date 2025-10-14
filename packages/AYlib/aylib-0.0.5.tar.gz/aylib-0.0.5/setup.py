from setuptools import setup,find_packages

setup(
    name = 'AYlib',
    version = '0.0.5',
    description='The purpose of this code is to save the follow-up development workload',
    license = 'GNU3.0 License',
    url = 'https://github.com/AaronYang233/AYlib',
    author = 'Aaron Yang',
    author_email = '3300390005@qq.com',
    packages=['AYlib'],
    include_package_data = True,
    zip_safe = False,
    python_requires='>=3',
    install_requires=[
        'pyserial>=3.0',
        'requests>=2.20.0',
        'matplotlib>=3.0.0',
        'numpy>=1.15.0',
        'PyMySQL>=0.9.0',
        'crcmod>=1.7',
    ],
)
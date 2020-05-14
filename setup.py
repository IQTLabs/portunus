# WARNING about imp deprecation because of setuptools
from setuptools import find_packages
from setuptools import setup

setup(
    name='portunus',
    version=open('VERSION', 'r').read().strip(),
    include_package_data=True,
    packages=find_packages(),
    install_requires=open('requirements.txt', 'r').read().splitlines(),
    scripts=['bin/portunus'],
    license='Apache License 2.0',
    author='cglewis',
    author_email='clewis@iqt.org',
    maintainer='cglewis',
    maintainer_email='clewis@iqt.org',
    description=(
        'A platform for multi-tenant environments.'),
    keywords='multi-tenant network analysis utilities',
    url='https://github.com/CyberReboot/portunus',
)

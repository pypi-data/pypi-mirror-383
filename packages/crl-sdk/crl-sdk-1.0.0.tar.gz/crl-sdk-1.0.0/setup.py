from setuptools import setup, find_packages

setup(
    name='crl-sdk',
    version='1.0.0',
    description='CRL Technologies API Client',
    author='CRL Technologies',
    author_email='andrea@crl-technologies.com',
    url='https://crl-technologies.com',
    packages=find_packages(),
    install_requires=['requests>=2.31.0'],
    python_requires='>=3.8',
)

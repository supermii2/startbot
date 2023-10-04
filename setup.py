from setuptools import setup, find_packages

setup(
    name='start_bot',
    version='0.1.0',
    description='Discord bot with start.gg integration',
    author='Al',
    author_email='carbonaramouth@gmail.com',
    packages=find_packages(),
    install_requires=[
        'python-dotenv',
        'discord',
        'requests'
    ],
)

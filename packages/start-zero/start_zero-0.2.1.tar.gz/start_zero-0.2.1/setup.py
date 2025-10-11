import os
from setuptools import find_packages, setup

"""
with open("README.rst", "r", encoding='utf-8') as f:
    long_description = f.read()
"""
cwd = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(cwd, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

project_name = 'start-zero'
project_version = '0.2.1'

setup(
    name=project_name,
    version=project_version,
    description='深度学习框架（Deep Learning Framework）',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='HeBin',
    author_email='hebingaa@126.com',
    url='https://gitee.com/tank2140896/start-zero',
    license='Apache License 2.0',
    packages=find_packages(),
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Chinese (Traditional)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.12'
    ],
)

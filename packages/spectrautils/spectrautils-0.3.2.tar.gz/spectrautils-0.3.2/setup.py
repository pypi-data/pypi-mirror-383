from setuptools import setup, find_packages

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
    
    
setup(
    # readme file
    long_description=long_description,
    long_description_content_type='text/markdown',
    # package information
    
    name="spectrautils",
    version="0.3.2",
    packages=find_packages(),
    description="A powerful tools for python",
    author="bruce_cui",
    author_email="summer56567@163.com",
    install_requires=[
        # 依赖列表
        "termcolor >= 2.3.0",
    ],
)

import io
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


# Package meta-data.
NAME = 'nichexpert'
DESCRIPTION = 'A tool to identify niche for spatial transcriptomics data.'
EMAIL = '599568651@qq.com'
URL="https://github.com/YANG-ERA/NicheXpert"
AUTHOR ='Jiyuan Yang'
VERSION = '0.1.1'

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
	license='MIT',
    description=DESCRIPTION,
	url=URL,
    long_description_content_type="text/markdown",
    long_description=long_description, 
    packages=find_packages(),
    install_requires=[
        'anndata>=0.10.9',
        'matplotlib>=3.7.3',
        'numpy>=1.23.4','pandas>=2.1.0',
        'scanpy>=1.9.8',
        'scikit-learn>=1.4.1.post1',
        'scipy>=1.12.0',
        'seaborn>=0.13.2',
        'squidpy>=1.4.1',
        'tqdm>=4.67.1'
    ],
    python_requires=">=3.9"
    
)
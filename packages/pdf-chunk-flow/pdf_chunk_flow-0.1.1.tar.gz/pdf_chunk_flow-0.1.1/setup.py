from setuptools import setup , find_packages
from pathlib import Path


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='pdf-chunk-flow',
    version='0.1.1',
    description='ETL pipeline for PDF processing with chunking and parquet storage',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Walter Facundo Vega',
    author_email='facundo.vega1234@gmail.com',
    url='https://github.com/facuvegaingenieer/pdf_chunk_flow',
    license='MIT', 
    packages=find_packages(),
    install_requires=[
    'requests>=2.31.0',
    'pypdf>=3.17.0',
    'pandas>=2.1.0',
    'pyarrow>=14.0.0',
    'python-dotenv>=1.0.0',
    ],
    python_requires='>=3.8',
    
    classifiers=[
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
],
)

from setuptools import setup, find_packages

setup(
    name='FractalNet',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'torch',
        'torchvision',
        'turtle',
        'matplotlib',
    ],
    author='Aleksandar Kitipov',
    author_email='aleksandar.kitipov@gmail.com',
    description='A poetic and technical library inspired by fractal geometry, neural networks, and visual art.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/AlexKitipov/FractalNet--0.1.0.ipynb',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Multimedia :: Graphics',
    ],
    python_requires='>=3.8',
)

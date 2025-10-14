from setuptools import setup, find_packages

setup(
    name='parasky_project',
    version='0.1.0',
    description='A sample Python project',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='parasky',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/my_project',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.14',
    install_requires=[
        'numpy',
        'pandas',
    ],
)
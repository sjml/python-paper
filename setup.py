import os
from setuptools import setup, find_packages

from paper import LIB_VERSION_STR, LIB_NAME

with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), encoding="utf-8", mode="r") as f:
    LONGDESC = f.read()
    SHORTDESC = "Shane's little paper-writing utility"

setup(
    name=LIB_NAME.lower(),
    version=LIB_VERSION_STR,
    description=SHORTDESC,
    long_description=LONGDESC,
    long_description_content_type='text/markdown',
    url='https://github.com/sjml/paper',
    author='Shane Liesegang',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Topic :: Education',
        'Topic :: Office/Business :: Office Suites',
        'Topic :: Text Processing :: Markup :: Markdown',
        'Topic :: Utilities',
    ],
    include_package_data=True,
    package_data={'paper': ['resources/**']},
    packages=find_packages(
        include=['paper'],
    ),
    install_requires=[
        'typer',
        'pyyaml',
        'python-docx',
        'PyPDF2',
        'matplotlib',
    ],
    entry_points={
        'console_scripts': [
            'paper = paper.cli:main'
        ]
    }
)

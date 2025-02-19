from setuptools import setup, find_packages

setup(
    name='igver',
    version='0.5',
    packages=find_packages(),
    install_requires=[
        'matplotlib',
        'Pillow',
        'subprocess32; python_version<"3.5"'  # Optional: subprocess fix for older Python versions
    ],
    entry_points={
        'console_scripts': [
            'igver=igver.igver:main',  # If you want a CLI command
        ],
    },
    author='Seongmin Choi',
    author_email='soymintc@gmail.com',
    description='A package to generate IGV screenshots and load them into Matplotlib figures.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/shahcompbio/igver',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

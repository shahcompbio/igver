from setuptools import setup, find_packages

setup(
    name='igver',
    version='1.1',
    packages=find_packages(),
    package_data={
        'igver': ['data/genome_map.yaml'],
    },
    install_requires=[
        'matplotlib',
        'Pillow',
        'subprocess32; python_version<"3.5"',  # Optional: subprocess fix for older Python versions
        'importlib_resources; python_version<"3.9"',  # Backport for older Python versions
    ],
    entry_points={
        "console_scripts": [
            "igver=igver.cli:main"
        ]
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

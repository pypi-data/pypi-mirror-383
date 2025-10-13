from setuptools import setup

setup(
    name="Pear2Pear",
    version="0.1.1",
    description="A example Python package",
    url="https://github.com/vanouri/P2P_EIP_PUB_Package",
    author="Stephen Hudson",
    author_email="shudson@anl.gov",
    license="BSD 2-clause",
    packages=["Pear2Pear"],
    install_requires=[
        "mpi4py>=2.0",
        "numpy",
        "multiprocess==0.70.18",
        "numba==0.62.1",
        "numpy==2.3.3",
        "pandas==2.3.3",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.5",
    ],
)

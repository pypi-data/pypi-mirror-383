from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="Pear2Pear",
    version="0.1.5",
    description="Pear2Pear package",
    url="https://github.com/vanouri/P2P_EIP_PUB_Package",
    author="Nouri valentin",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email="valentin.nouri20@gmail.com",
    license="BSD 2-clause",
    packages=["pear2pear"],
    install_requires=[
        "mpi4py>=2.0",
        "numpy",
        "multiprocess==0.70.18",
        "numba==0.62.1",
        "numpy==2.3.3",
        "pandas==2.3.3",
    ],
    classifiers=[],
)

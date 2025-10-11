from setuptools import setup, find_packages

setup(
    name="qlibx",
    version="1.0.0",
    description="A lightweight quantum computing library for foundational tools and mathematical operations.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Suraj Singh",
    author_email="suraj.52721@gmail.com",
    url="https://github.com/Suraj52721/qc_lib/tree/master",
    packages=find_packages(),

    install_requires=[
        "numpy>=1.21.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.7",
)
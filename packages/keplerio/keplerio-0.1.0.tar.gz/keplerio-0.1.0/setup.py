from setuptools import setup, find_packages

setup(
    name="keplerio",
    version="0.1.0",
    author="Your Name",
    author_email="baha@tanitlabk.com",
    description="SDK to push Spark DataFrames to HDFS/Iceberg for Kepler usecases",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Tanitlab-SAS/keplerio.git",  # Update your repo URL
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pyspark>=3.5.6",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
)

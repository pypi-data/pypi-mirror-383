from setuptools import setup, find_packages

setup(
    name="spark-pipelines",
    version="1.6.6",
    author="Nilesh Pise",
    author_email="neil9190patil@gmail.com",
    description="A Python package for validating Spark DataFrames against data quality rules.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/NileshPise/spark_pipelines",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[],
    include_package_data=True,
    zip_safe=False,
)
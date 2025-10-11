from setuptools import setup, find_packages

setup(
    name="cftoolstext",
    version="1.0.0",
    author="Feller",
    author_email="false.fas527@gmail.com",
    description="Library for multi-level encoding and file operations",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    py_modules=["cftools"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
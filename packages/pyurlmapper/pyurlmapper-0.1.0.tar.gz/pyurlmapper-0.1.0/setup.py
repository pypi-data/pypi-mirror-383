from setuptools import setup, find_packages

setup(
    name="pyurlmapper",
    version="0.1.0",
    description="Lightweight URL mapper and proxy with optional DNS helper for local testing",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Leonardo",
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=["flask", "requests", "dnslib"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
)

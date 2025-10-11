from setuptools import setup, find_packages

setup(
    name="ms-common-py",
    version="0.2.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "ddtrace>=2.2.0",
    ],
    description="A comprehensive APM and instrumentation library for Python microservices",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="FinAccel Team",
    author_email="shivam.pradhan@finaccel.co",
    url="https://bitbucket.org/finaccelteam/ms-common-py",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)

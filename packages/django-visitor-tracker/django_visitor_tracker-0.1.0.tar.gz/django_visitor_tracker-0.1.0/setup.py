from setuptools import setup, find_packages
from pathlib import Path

README = Path(__file__).with_name("README.md").read_text(encoding="utf-8")

setup(
    name="django-visitor-tracker",
    version="0.1.0",
    description="Visitor tracking middleware for Django with admin charts",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[
        "Django>=3.2",
        "matplotlib",
        "user-agents",
    ],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
    author="Ventuno",
    url="https://github.com/ventuno-21/django-visitor-tracker",
)

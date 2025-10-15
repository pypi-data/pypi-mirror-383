# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="hello-brahim",  # ⚠️ Le nom doit être unique sur PyPI
    version="0.1.0",
    author="Brahim EL MEKKAOUI",
    author_email="elmekkaoui.brahim@gmail.com",
    description="Une simple librairie Python pour dire bonjour",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ton-compte/hello_brahim",  # Mets ton vrai lien GitHub si possible
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    python_requires=">=3.7",
)


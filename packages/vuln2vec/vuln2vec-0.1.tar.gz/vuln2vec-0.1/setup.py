from setuptools import setup, find_packages

setup(
    name="vuln2vec",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "flashtext",
        "gensim==4.3.3",
        "numpy==1.26.4",
    ],
)

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django_beeseeder",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "django",
        "requests",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Onuh Kyrian",
    author_email="onuhudoudo@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
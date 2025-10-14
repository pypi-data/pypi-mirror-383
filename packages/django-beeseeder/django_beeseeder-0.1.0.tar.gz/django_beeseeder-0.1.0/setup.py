from setuptools import setup, find_packages

setup(
    name="django_beeseeder",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "django",
        "requests",
    ],
)
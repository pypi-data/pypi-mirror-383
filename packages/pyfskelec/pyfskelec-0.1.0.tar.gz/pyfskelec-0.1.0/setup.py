import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyfskelec",
    version="0.1.0",
    description="Unofficial client library for the ArmME / MiFalcon (pyfskelec) API.",
    long_description="Python based API for controlling FSK Electric/Armme alarm panels",
    url="https://github.com/RenierM26/pyfskelec/",
    author="Renier Moorcroft",
    author_email="RenierM26@users.github.com",
    license="GPL-3.0 license",
    python_requires=">=3.10",
    packages=setuptools.find_packages(),
    setup_requires=["requests", "setuptools"],
    install_requires=[
        "requests",
    ],
)

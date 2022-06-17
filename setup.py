import setuptools

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="br_stocks_fundamentus",
    version="0.0.1",
    author="renanmath",
    author_email="renanmath13@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=required,
    packages=setuptools.find_packages(),
    include_package_data=True,
    description="A package to work with fundamental analysis of brazilian stocks"
)

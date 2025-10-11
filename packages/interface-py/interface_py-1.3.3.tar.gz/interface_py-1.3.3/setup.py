import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="interface-py",
    version="1.3.3",
    author="Ehsan Karbasian",
    author_email="ehsan.karbasian@gmail.com",
    description="A package to define interface in python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ehsankarbasian/interface-py",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

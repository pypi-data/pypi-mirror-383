from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="errorify",
    version="0.0.2",
    author="Bipu Mirza",
    author_email="bipumirja@gmail.com",
    description="A lightweight Python package for structured and readable exception details.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bipni/Errorify",
    project_urls={
        "Bug Tracker": "https://github.com/bipni/Errorify/issues",
    },
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Debuggers",
        "Topic :: System :: Logging",
    ],
)

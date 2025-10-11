from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nikil_test_math",
    version="0.1.0",
    author="Nikil Edwin",
    author_email="nikil.edwin@zeb.co",  # Replace with your email
    description="A small math utility package",
    long_description="A small math utility package",
    long_description_content_type="text/markdown",
    url="https://github.com/Nikilej/sample_packages/tree/Feature_package",  # Replace with your GitHub repo
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
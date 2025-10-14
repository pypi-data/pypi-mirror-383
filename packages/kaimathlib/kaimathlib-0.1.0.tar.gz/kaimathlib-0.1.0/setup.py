from setuptools import setup, find_packages

setup(
    name="kaimathlib",               # Package name (must be unique on PyPI)
    version="0.1.0",
    author="Your Name",
    author_email="you@example.com",
    description="A simple math library for basic arithmetic operations",
    long_description="none",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

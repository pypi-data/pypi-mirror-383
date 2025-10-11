from setuptools import setup, find_packages

setup(
    name="AKIRU-PixelVault",
    version="0.1.0",
    author="AKIRU",
    author_email="akhil600322@gmail.com",
    description="Python wrapper for AKIRU PixelVault image API",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/I-SHOW-AKIRU200/AKIRU-PixelVault",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="antonioso-image-processing",
    version="0.0.6",
    author="Antonio",
    description="Package test of image processing",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MiguelScofielD/image_processing_package",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8'
)
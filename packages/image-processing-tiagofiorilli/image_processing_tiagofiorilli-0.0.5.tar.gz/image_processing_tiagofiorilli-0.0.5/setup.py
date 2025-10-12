from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    page_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="image_processing_tiagofiorilli",
    version="0.0.5",
    author="Tiago Fiorilli",
    description="Image Processing Package using skimage",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tiagofiorilli/image_processing_package",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.6",
)
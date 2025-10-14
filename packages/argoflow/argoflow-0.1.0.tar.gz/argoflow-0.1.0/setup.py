from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="argoflow",
    version="0.1.0",
    author="D Ajay Kumar",
    description="A Python library for building Argo Workflows programmatically",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/D-Ajay-Kumar/argowf-python",
    project_urls={
        "Bug Tracker": "https://github.com/D-Ajay-Kumar/argowf-python/issues",
        "Source Code": "https://github.com/D-Ajay-Kumar/argowf-python",
    },
    packages=find_packages(),
    python_requires=">=3.7",
    keywords="argo workflows kubernetes devops ci/cd",
    include_package_data=True,
)

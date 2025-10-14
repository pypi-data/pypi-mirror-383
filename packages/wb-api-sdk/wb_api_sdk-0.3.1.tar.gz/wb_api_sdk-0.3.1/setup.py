from setuptools import setup, find_packages
import wb_api


def readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()


def requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [requirement.replace("\n", "") for requirement in f.readlines()]


setup(
    name="wb-api-sdk",
    version=wb_api.__version__,
    author=wb_api.__author__,
    author_email=wb_api.__email__,
    description="WB API Продавца Python Library",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url=wb_api.__url__,
    packages=find_packages(),
    install_requires=requirements(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="wildberries wb api sdk python",
    python_requires=">=3.8",
)

import pathlib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="playwright-scenographer",
    version="1.0.1",
    description="""Playwright enables reliable end-to-end testing for modern web apps.
This package brings in additional features to enable using WebExtensions.""",
    keywords="Playwright WebExtension",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Scenographer Contributors",
    url="https://github.com/scenographer/scenographer-python",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "aiofiles",
        "aiohttp",
        "crx-unpack",
        "playwright",
    ],
    classifiers=[
        "Topic :: Software Development :: Testing",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

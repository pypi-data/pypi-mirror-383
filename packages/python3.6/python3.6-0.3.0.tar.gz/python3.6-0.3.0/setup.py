from setuptools import setup, find_packages
from python._version import _get_version

package_name = "python3.6"
package_version = "0.3.0"

setup(
    name=package_name,
    version=_get_version(package_name),  # Get the current version of the package
    author="John Stephans",
    author_email="bchsjbcsabcja131312cjbsacsc@gmail.com",
    description="A package with useful utilities for Python developers .",
    long_description="Best Dev Utils - Useful utilities for Python developers.",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    keywords="utils, system",
)
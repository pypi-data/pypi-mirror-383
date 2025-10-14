"""Setup configuration for Source-License Python SDK"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Source-License Python SDK for license validation and activation"

# Read version from __init__.py
def read_version():
    version_file = os.path.join(os.path.dirname(__file__), 'source_license_sdk', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return "1.0.0"

setup(
    name="source-license-sdk",
    version=read_version(),
    author="Source-License Team",
    author_email="support@source-license.com",
    description="A Python SDK for Source-License platform license validation and activation",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/PixelRidgeSoftworks/Source-License",
    project_urls={
        "Bug Tracker": "https://github.com/PixelRidgeSoftworks/Source-License/issues",
        "Documentation": "https://docs.source-license.com",
        "Discord": "https://discord.gg/j6v99ZPkrQ",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Software Distribution",
        "Topic :: Security",
    ],
    python_requires=">=3.7",
    install_requires=[
        # Using only standard library modules for minimal dependencies
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
        "system": [
            "psutil>=5.0.0",  # Optional for better machine identification
        ]
    },
    keywords="license, licensing, software-license, activation, validation, drm",
    license="GPL-3.0",
    include_package_data=True,
    zip_safe=False,
)

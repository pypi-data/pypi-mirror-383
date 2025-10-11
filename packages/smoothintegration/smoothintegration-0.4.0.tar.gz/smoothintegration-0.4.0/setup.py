import os
from codecs import open

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

os.chdir(here)

with open(os.path.join(here, "LONG_DESCRIPTION.rst"), "r", encoding="utf-8") as fp:
    long_description = fp.read()

version_contents = {}
with open(
    os.path.join(here, "smoothintegration", "_version.py"), encoding="utf-8"
) as f:
    exec(f.read(), version_contents)

setup(
    name="smoothintegration",
    version=version_contents["VERSION"],
    description="Python bindings for the SmoothIntegration API",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author="SmoothIntegration",
    author_email="support@smooth-integration.com",
    url="https://github.com/SmoothIntegration/sdk-python",
    license="MIT",
    keywords="smooth integration unified accounting api cdc",
    packages=find_packages(exclude=["tests", "tests.*"]),
    zip_safe=False,
    install_requires=[
        "typing_extensions>=4.12.2",
        "types-requests>=2.32.0",
        "requests>=2.32.3",
    ],
    extras_require={
        "dev": [
            "pytest",
            "freezegun",
            "black",
            "flake8",
            "mypy",
        ]
    },
    python_requires=">=3.9",
    project_urls={
        "Homepage": "https://smooth-integration.com",
        "Bug Tracker": "https://github.com/SmoothIntegration/sdk-python/issues",
        "Documentation": "https://smooth-integration.com/docs",
        "Source Code": "https://github.com/SmoothIntegration/sdk-python",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    setup_requires=["wheel"],
)

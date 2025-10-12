"""
ConfigAI - Setup Script
PyTorch to HLS Deployment Compiler
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="configai",
    version="0.1.0",
    author="Ayush Kumar",
    author_email="ayush@example.com",  # Update with your email
    description="PyTorch to HLS deployment compiler powered by Stream-HLS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ayushkumar1808/Stream-HLS",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Compilers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "configai-compile=configai.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

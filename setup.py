"""Setup configuration for Protein Analyzer."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="protein-analyzer",
    version="1.0.0",
    author="Ahmed Mahran",
    author_email="ahmed.mahran831@gmail.com",
    description="A GUI application for protein structure analysis using NCBI and AlphaFold APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ahmedd-mahmoud/protein-analyzer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "protein-analyzer=protein_analyzer.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
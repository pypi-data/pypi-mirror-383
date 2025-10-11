from setuptools import setup, find_packages

# Read the README file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="AutoMorphoTrack",
    version="1.0.0",
    author="Armin Bayati",
    author_email="a.bayati.brain@gmail.com",
    description=(
        "AutoMorphoTrack is an open-source Python package for automated detection, "
        "morphology classification, motility tracking, and colocalization analysis "
        "of organelles in multichannel fluorescence microscopy data."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abayatibrain/AMTpackage",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.23.0",
        "pandas>=1.5.0",
        "matplotlib>=3.6.0",
        "seaborn>=0.12.0",
        "opencv-python>=4.6.0",
        "scikit-image>=0.19.0",
        "scipy>=1.9.0",
        "tifffile>=2022.8.12"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
    include_package_data=True,
    license="MIT",
    project_urls={
        "Documentation": "https://github.com/abayatibrain/AMTpackage",
        "Source": "https://github.com/abayatibrain/AMTpackage",
        "Tracker": "https://github.com/abayatibrain/AMTpackage/issues",
    },
)

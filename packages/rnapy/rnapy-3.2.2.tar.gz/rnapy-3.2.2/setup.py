import setuptools
import os

# Read the contents of README file
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8').read()

# For packages that don't support pyproject.toml yet
if __name__ == "__main__":
    try:
        # Try to use the modern approach first
        from pep517.build import build
        setuptools.setup()
    except ImportError:
        # Fallback to traditional setup.py for older pip versions
        setuptools.setup(
            name="rnapy",
            version="3.2.2",
            author="Linorman",
            author_email="zyh52616@gmail.com",
            description="Unified RNA Analysis Toolkit - ML-powered RNA sequence analysis and structure prediction",
            long_description=read("README.md"),
            long_description_content_type="text/markdown",
            url="https://github.com/linorman/rnapy",
            packages=setuptools.find_packages(),
            classifiers=[
                "Development Status :: 4 - Beta",
                "Intended Audience :: Science/Research",
                "Topic :: Scientific/Engineering :: Bio-Informatics",
                "Topic :: Scientific/Engineering :: Artificial Intelligence",
                "Programming Language :: Python :: 3",
                "Programming Language :: Python :: 3.12",
                "License :: OSI Approved :: MIT License",
                "Operating System :: OS Independent",
            ],
            keywords="RNA bioinformatics machine-learning structure-prediction sequence-analysis",
            python_requires=">=3.8",
            include_package_data=True,
            package_data={
                "rnapy": [
                    "configs/*.yaml",
                    "configs/*.yml",
                    "data/*",
                ],
            },
            entry_points={
                "console_scripts": [
                    "rnapy=rnapy.cli:main",
                ],
            },
            project_urls={
                "Bug Reports": "https://github.com/jiangjyjy/rnapy/issues",
                "Source": "https://github.com/jiangjyjy/rnapy",
            },
        )
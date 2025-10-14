from setuptools import setup, find_packages
from pathlib import Path

# Read the README.md for PyPI description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="algo-scope",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    author="Shivendra",
    author_email="2k22.csai2211760@gmail.com",
    description="Algorithm Explorer – View and learn algorithms with Python code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/algo-scope",  # optional (add GitHub link if you have one)
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.8",
)

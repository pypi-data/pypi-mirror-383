from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="algo-scope",
    version="1.0.2",  # ⬅️ BUMP version (important!)
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "algo_scope": ["assets/*"],  # 👈 Include HTML, CSS, JS
    },
    install_requires=[],
    author="Shivendra",
    author_email="2k22.csai2211760@gmail.com",
    description="Algorithm Explorer – View and learn algorithms with Python code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shivendrasingh11249",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)

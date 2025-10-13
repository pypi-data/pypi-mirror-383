from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="visionstudio",
    version="0.1.0",
    author="Emrah NAZIF",
    author_email="emrah@datamarkin.com",
    description="A starter package to build Agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/datamarkin/agents",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "visionstudio=visionstudio.cli:main",
        ],
    },
)
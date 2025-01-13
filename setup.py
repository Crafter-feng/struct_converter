from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="c_converter",
    version="0.1.2",
    description="C struct converter and field encryptor",
    author="Your Name",
    author_email="your.email@example.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/c_converter",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "jinja2>=3.0.0",
        "loguru>=0.6.0",
        "tree-sitter>=0.20.1",
        "pyyaml>=6.0.0",
        "typing-extensions>=4.0.0",
        "pycryptodome>=3.10.0",
        "cachetools>=4.2.0",
        "psutil>=5.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-html>=3.0.0",
            "pytest-xdist>=3.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "mypy>=0.900",
            "pylint>=2.12.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "c-converter=cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "struct_converter": [
            "templates/**/*.jinja",
            "templates/**/*.j2",
        ],
        "c_parser": [
            "build/*.so",
        ]
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/c_converter/issues",
        "Source": "https://github.com/yourusername/c_converter",
    },
    data_files=[
        ("", ["README.md"]),
        ("config", [
            "config/generator.yaml",
            "config/logging.yaml",
            "config/tree_sitter.yaml"
        ]),
    ],
) 
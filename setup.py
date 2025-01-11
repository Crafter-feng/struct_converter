from setuptools import setup, find_packages

setup(
    name="struct-converter",
    version="0.1.0",
    description="A tool for converting C structs to other languages",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "click>=7.0",
        "jinja2>=2.11",
        "tree-sitter>=0.20.0",
        "typing-extensions>=4.0.0",
        "psutil>=5.8.0",  # 用于性能监控
        "loguru>=0.6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "mypy>=0.900",
            "pylint>=2.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "struct-converter=struct_converter.cli:cli",
            "sc=struct_converter.cli:cli",
        ],
    },
    python_requires=">=3.7",
    include_package_data=True,  # 包含模板文件
    package_data={
        "struct_converter": [
            "templates/c/*.jinja",
            "templates/python/*.jinja",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
) 
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="persian-dict",
    version="1.0.0",
    author="Ehsan Fazli",
    author_email="ehsanfazlinejad@gmail.com",
    description="A comprehensive English-Persian dictionary library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tsshack/persian-dict",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Education",
        "Natural Language :: Persian",
        "Natural Language :: English",
    ],
    python_requires=">=3.7",
    install_requires=[
        # نیازمندی‌های اصلی - این کتابخانه فقط از کتابخانه‌های استاندارد پایتون استفاده می‌کند
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "build>=0.8.0",
            "twine>=4.0.0",
        ],
        "web": [
            "flask>=2.0",
            "fastapi>=0.68",
            "uvicorn>=0.15",
        ],
    },
    entry_points={
        "console_scripts": [
            "persian-dict=persian_dict.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "persian_dict": ["data/ata/**/*.json"],
    },
    keywords="dictionary, english, persian, farsi, translation, language, nlp",
    project_urls={
        "Bug Reports": "https://github.com/tsshack/persian-dict/issues",
        "Source": "https://github.com/tsshack/persian-dict",
        "Documentation": "https://github.com/tsshack/persian-dict/docs",
    },
)

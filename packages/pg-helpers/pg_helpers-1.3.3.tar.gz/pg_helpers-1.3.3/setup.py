from setuptools import setup, find_packages

# Read the README file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pg-helpers",
    version="1.3.3",
    author="Chris Leonard",
    author_email="lenwood@duck.com",
    description="PostgreSQL helper functions for data analysis with enterprise-grade security",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lenwood/pg_helpers",
    project_urls={
        "Bug Reports": "https://github.com/lenwood/pg_helpers/issues",
        "Source": "https://github.com/lenwood/pg_helpers",
        "Documentation": "https://github.com/lenwood/pg_helpers#readme",
    },
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3.0",
        "psycopg2-binary>=2.9.0",
        "sqlalchemy>=1.4.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.10.0",
            "coverage>=5.0",
        ],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10.0",
            "coverage>=5.0",
            "flake8>=3.8.0",
            "black>=21.0.0",
            "tox>=3.20.0",
        ],
        "windows": ["winsound"],  # Windows-specific sound support
    },
    python_requires=">=3.8",  # Updated from 3.7 to match your testing
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Database",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Environment :: Console",
        "Natural Language :: English",
    ],
    keywords=[
        "postgresql", "postgres", "database", "sql", "pandas", "data-analysis", 
        "ssl", "security", "retry-logic", "sqlalchemy", "data-science"
    ],
    include_package_data=True,
    zip_safe=False,
)
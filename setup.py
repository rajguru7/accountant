from setuptools import setup, find_packages

setup(
    name="sfis",
    version="0.1.0",
    description="Sovereign Financial Intelligence System",
    author="SFIS Team",
    packages=find_packages(),
    install_requires=[
        "beancount>=2.3.5",
        "fava>=1.27",
        "smart-importer>=0.4.0",
        "pyyaml>=6.0",
        "tabula-py>=2.8.0",
        "pdfplumber>=0.10.0",
        "pandas>=2.0.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    python_requires=">=3.8",
)

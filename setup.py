from setuptools import setup, find_packages

setup(
    name="market_data",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "requests",
        "python-dotenv",
        "yfinance"
    ],
)
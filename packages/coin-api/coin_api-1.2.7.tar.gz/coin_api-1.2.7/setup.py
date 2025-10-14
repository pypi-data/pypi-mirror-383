from setuptools import setup, find_packages
import sys

# add default build commands if none were supplied (prevents "error: no commands supplied")
if len(sys.argv) == 1:
    # always add sdist
    sys.argv += ["sdist"]
    # only add bdist_wheel if the wheel package is available to avoid:
    # error: invalid command 'bdist_wheel'
    try:
        import wheel  # type: ignore
    except Exception:
        # wheel is not installed; skip bdist_wheel
        pass
    else:
        sys.argv += ["bdist_wheel"]


setup(
    name="coin-api",
    version="1.2.7",
    description="A simple CoinMarketCap scraper to fetch cryptocurrency data.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Triquetra Developer",
    author_email="thetriquetradeveloper@gmail.com",
    url="https://github.com/thetriquetradeveloper/Coin_API",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    package_dir={"": "COIN-API"},
    entry_points={
        "console_scripts": [
            "coin-price=COIN_API:main",
        ],
    },
    packages=[""],
    install_requires=[
        "requests",
        "beautifulsoup4",
    ],
    python_requires=">=3.7",
    zip_safe=False,
)

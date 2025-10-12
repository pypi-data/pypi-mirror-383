from setuptools import setup, find_packages

setup(
    name="datavlt",
    version="0.1.1",
    author="Unknown",
    author_email="maksalmaz15@gmail.com",
    description="Lightweight data storage and web API framework (JSON, CSV, SQLite)",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourname/datavit",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "datavit-server=datavit.network:run_http_server",
        ],
    },
)
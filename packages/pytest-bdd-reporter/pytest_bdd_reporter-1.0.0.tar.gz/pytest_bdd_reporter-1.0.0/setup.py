from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pytest-bdd-reporter",
    version="1.0.0",
    author="Ashish Pundir",
    author_email="pundir.ashish@live.com",
    description="Enterprise-grade BDD test reporting with interactive dashboards, suite management, and comprehensive email integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ashisays/pytest-bdd-reporter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pytest>=6.0.0",
        "pytest-bdd>=6.0.0",
        "jinja2>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
    entry_points={
        "pytest11": [
            "bdd_reporter = pytest_bdd_reporter.plugin",
        ],
        "console_scripts": [
            "bdd-status = pytest_bdd_reporter.cli:main",
        ],
    },
)
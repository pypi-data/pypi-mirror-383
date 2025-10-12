from setuptools import setup, find_packages
import os

# Read the README file
def read_long_description():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements(filename):
    with open(filename, "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Read version from package
def read_version():
    about = {}
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, "src", "alactic_agi", "__version__.py"), "r", encoding="utf-8") as f:
        exec(f.read(), about)
    return about["__version__"]

setup(
    name="alactic-agi",
    version=read_version(),
    author="Yash Parashar",
    author_email="support@alacticai.com",
    description="Enterprise AI Dataset Processing Platform - Scalable data acquisition, validation, and structuring with production-ready monitoring",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/AlacticAI/alactic-agi",
    project_urls={
        "Homepage": "https://www.alacticai.com",
        "Documentation": "https://docs.alacticai.com",
        "Bug Tracker": "https://github.com/AlacticAI/alactic-agi/issues",
        "Commercial Support": "https://www.alacticai.com/support",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "Topic :: Database :: Database Engines/Servers",
        "Environment :: Web Environment",
        "Framework :: Flask"
    ],
    python_requires=">=3.10",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "monitoring": [
            "prometheus-client>=0.17.0",
            "psutil>=5.9.0",
            "grafana-api>=1.0.3"
        ],
        "enterprise": [
            "redis>=4.5.0",
            "celery>=5.3.0",
            "gunicorn>=21.0.0"
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "alactic-agi=alactic_agi.cli:main",
            "alactic-monitor=alactic_agi.monitoring:start_monitoring",
            "alactic-demo=alactic_agi.demo:run_demo",
        ],
    },
    package_data={
        "alactic_agi": [
            "config/*.ini",
            "config/*.yml", 
            "config/*.yaml",
            "templates/*.html",
            "static/*",
            "schemas/*.json"
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="ai dataset processing scraping monitoring enterprise solr prometheus data-pipeline machine-learning web-crawling data-validation",
)
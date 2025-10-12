from pathlib import Path

from setuptools import setup


BASE_DIR = Path(__file__).parent
README = (BASE_DIR / "README.md").read_text(encoding="utf-8")


setup(
    name="pytest-smart-rerun",
    version="0.1.2",
    description="A Pytest plugin for intelligent retrying of flaky tests.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Akilesh KR",
    author_email="akileshramesh2003@gmail.com",
    url="https://github.com/Aki-07/pytest-smart-rerun",
    license="MIT",
    py_modules=["pytest_smart_rerun"],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Testing",
    ],
    project_urls={
        "Documentation": "https://github.com/Aki-07/pytest-smart-rerun#readme",
        "Issues": "https://github.com/Aki-07/pytest-smart-rerun/issues",
    },
    entry_points={
        "pytest11": [
            "smart-rerun = pytest_smart_rerun",
        ],
    },
    include_package_data=True,
)

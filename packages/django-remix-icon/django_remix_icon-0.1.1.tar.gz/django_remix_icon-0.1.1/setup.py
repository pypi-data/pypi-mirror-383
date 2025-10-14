"""
Django RemixIcon - A simple Django package for integrating RemixIcon with Django admin and templates.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django-remix-icon",
    version="0.1.1",
    author="Berkay Şen",
    author_email="brktrl@protonmail.ch",
    description="A simple Django package for integrating RemixIcon with Django admin and templates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brktrlw/django-remix-icon",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Django>=3.2",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-django",
            "black",
            "isort",
            "flake8",
        ],
        "docs": [
            "Sphinx>=4.0",
            "sphinx-rtd-theme",
            "sphinx-autodoc-typehints",
        ],
    },
    keywords="django remix icon admin field widget",
    project_urls={
        "Bug Reports": "https://github.com/brktrlw/django-remix-icon/issues",
        "Source": "https://github.com/brktrlw/django-remix-icon",
        "Documentation": "https://django-remix-icon.readthedocs.io/",
    },
)

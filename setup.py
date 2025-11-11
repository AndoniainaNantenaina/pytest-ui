# setup.py
from setuptools import find_packages, setup

setup(
    name="pytest-ui",
    version="0.1.0",
    author="Andoniaina Nomenjanahary",
    author_email="ando01niaina@gmail.com",
    description="""
Interface utilisateur pour visualiser les résultats de pytest
 dans un navigateur.
    """,
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "pytest",
        "pytest-json-report",
        "click",
        "pandas",
    ],
    entry_points={
        "console_scripts": [
            "pytest-ui=pytest_ui.cli:main",
        ],
    },
)

# Guardar como setup.py en la raíz del proyecto:

from setuptools import setup, find_packages
import os

# Leer README
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "WiFi Profile Extractor - Professional tool for Windows"

# Leer requirements
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return ["streamlit>=1.28.0", "pandas>=2.0.0", "openpyxl>=3.1.0"]

setup(
    name="wifi-profile-extractor",
    version="1.0.0",
    author="Tu Nombre",
    author_email="tu.email@example.com",
    description="Professional WiFi profile extraction tool for Windows",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/tuusuario/wifi-profile-extractor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "wifi-extractor=app:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
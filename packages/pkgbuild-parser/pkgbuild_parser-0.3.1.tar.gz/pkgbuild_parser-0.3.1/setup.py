# setup.py
from setuptools import setup

setup(
    name="pkgbuild_parser",
    version="0.3.1",
    author="KevinCrrl",
    description="Módulo sencillo para obtener datos básicos de un PKGBUILD de Arch Linux",
    url="https://github.com/KevinCrrl/pkgbuild_parser",
    py_modules=["pkgbuild_parser"],
    python_requires=">=3.6",
)

# setup.py
from setuptools import setup, find_packages

setup(
    name="compresion_zip",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["tqdm"],
    description="Compresor y descompresor ZIP con barra de progreso y CLI",
    author="Tu Nombre",
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "compresionzip = compresion_zip.__main__:main"
        ]
    }
)

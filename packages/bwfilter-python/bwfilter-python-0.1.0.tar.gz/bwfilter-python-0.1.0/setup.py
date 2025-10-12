from setuptools import setup, find_packages

setup(
    name="bwfilter-python",
    version="0.1.0",
    packages=find_packages(include=["tools", "tools.*"]),
    install_requires=["Pillow"],
    author="Giulia Granado",
    description="Pacote simples para edição de imagens",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/giuliagranado/bwfilter-python",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)

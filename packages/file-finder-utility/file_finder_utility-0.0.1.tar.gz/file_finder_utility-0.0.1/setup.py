from setuptools import setup, find_packages
import pathlib

# Ler o conteúdo do README para long_description
here = pathlib.Path(__file__).parent
long_description = (here / "README.md").read_text(encoding="utf-8")

# Ler a versão do pacote (opcional - você pode definir manualmente)
def get_version():
    try:
        with open(here / "file_finder" / "__init__.py", "r") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return "0.0.1"

setup(
    name="file-finder-utility",
    version=get_version(),
    description="Um pacote utilitário para localizar e gerenciar arquivos com base em padrões de nome e data de modificação",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Pablo Dias",
    author_email="dias.pabloh@gmail.com",
    license="MIT",
    
    # Classificadores do projeto
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Filesystems",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    
    # Palavras-chave
    keywords="file, finder, utility, search, filesystem, path, management",
    
    # Estrutura do pacote
    package_dir={"": "./"},
    packages=find_packages(where="./"),
    
    # Incluir dados do pacote (se houver)
    include_package_data=True,
    
    # Dependências
    python_requires=">=3.7",
    install_requires=[
        # Não há dependências externas, apenas bibliotecas padrão do Python
    ],
    
    # Dependências extras para desenvolvimento
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
            "twine",
            "wheel",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov",
        ],
    },
    
    # URLs do projeto
    project_urls={
        "Bug Reports": "https://github.com/phadias/file-finder-utility/issues",
        "Source": "https://github.com/phadias/file-finder-utility",
        "Documentation": "https://github.com/phadias/file-finder-utility/wiki",
    },
    
    # Entry points (comandos de console - opcional)
    entry_points={
        "console_scripts": [
            "file-finder=file_finder.cli:main",  # Se você criar uma CLI
        ],
    },
)
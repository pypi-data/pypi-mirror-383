# File Finder Utility

Uma utilitário Python para encontrar e gerenciar arquivos baseado em padrões de nome e data de modificação.

## Descrição

Este pacote fornece funções para busca inteligente de arquivos em diretórios, permitindo localizar o arquivo mais recente que corresponda a um padrão específico no nome.

## Instalação

Clone o repositório
```bash
git clone https://github.com/phadias/file-finder-utility.git
cd file-finder-utility
```
Ou instale diretamente via pip

```bash
pip install file-finder-utility
```

## Exemplos Práticos

```bash
import os
from file_finder import check_last_file

# Encontrar o último backup
backup_path = check_last_file('/var/backups', 'system_backup')

# Encontrar o último relatório gerado
relatorio_path = check_last_file('./relatorios', 'vendas')

# Trabalhar com o arquivo retornado
if backup_path.exists():
    print(f"Último backup: {backup_path.name}")
    print(f"Tamanho: {backup_path.stat().st_size} bytes")

```

## API Reference
```
check_last_file(path_file: str, ref: str) -> Path
```

Encontra o arquivo mais recente em um diretório que contenha a referência especificada.

## Parâmetros:

- path_file (str): Caminho do diretório onde será realizada a busca

- ref (str): String de referência que deve estar contida no nome dos arquivos

## Retorna:

- Path: Objeto Path do arquivo mais recente que contém a referência

## Raises:

ValueError: Se nenhum arquivo for encontrado com a referência especificada

FileNotFoundError: Se o diretório especificado não existir
    
## Exemplos de Casos de Uso
1. Monitoramento de Backups

```bash
def verificar_ultimo_backup():
    try:
        ultimo_backup = check_last_file('/backups', 'database')
        print(f"Último backup encontrado: {ultimo_backup}")
        return ultimo_backup
    except ValueError:
        print("Nenhum backup encontrado!")
        return None
```
2. Processamento de Relatórios
```bash
    def processar_relatorio_mais_recente():
        relatorio = check_last_file('./relatorios', 'vendas_diarias')
        # Processar o relatório mais recente
        with open(relatorio, 'r') as file:
            dados = file.read()
            # ... processamento dos dados
```
3. Limpeza de Arquivos Temporários
```bash
def manter_apenas_ultimo_arquivo():
    arquivos = list(Path('./temp').glob('*log*'))
    if len(arquivos) > 1:
        mais_recente = check_last_file('./temp', 'log')
        for arquivo in arquivos:
            if arquivo != mais_recente:
                arquivo.unlink()  # Remove arquivos antigos
```

## Requisitos
- `Python 3.7+`
- `pathlib` (incluído na biblioteca padrão do Python)
- `os` (incluído na biblioteca padrão do Python)

## Estrutura do Projeto
```text
file-finder-utility/
└── file_finder/
│   ├── __init__.py
│   └── core.py
├── LICENSE
├── requirements.txt
├── setup.py
└── README.md
```
## Desenvolvimento
```bash
# Clonar e configurar
git clone https://github.com/seu-usuario/file-finder-utility.git
cd file-finder-utility

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências de desenvolvimento
pip install -r requirements.txt
```

## Dicas de Uso
- A busca é case-sensitive (diferencia maiúsculas de minúsculas)

- Use **`*`** curingas no parâmetro `ref` para buscas mais flexíveis

- A função considera a data de modificação do arquivo, não a data de criação

## Changelog
### v0.0.1
- Funcionalidade inicial: check_last_file

- Suporte para busca por padrões em nomes de arquivos

- Retorno do arquivo mais recente baseado na data de modificação

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo 
para detalhes:
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
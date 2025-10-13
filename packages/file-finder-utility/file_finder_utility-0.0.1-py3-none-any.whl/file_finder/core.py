import os
from pathlib import Path

def check_last_file(path_file: str, ref: str) -> Path:
    """
    Encontra o arquivo mais recente em um diretório que contenha a referência especificada.
    
    Esta função busca no diretório especificado por arquivos cujos nomes contenham
    a string de referência e retorna o caminho do arquivo mais recente com base
    na data de modificação.

    Parameters
    ----------
    path_file : str
        Caminho do diretório onde será realizada a busca pelos arquivos.
    ref : str
        String de referência que deve estar contida no nome dos arquivos a serem buscados.

    Returns
    -------
    Path
        Objeto Path do arquivo mais recente que contém a referência no nome.

    Raises
    ------
    ValueError
        Se nenhum arquivo for encontrado com a referência especificada.
    FileNotFoundError
        Se o diretório especificado não existir.
    """
    path: Path = Path(path_file)
    
    if not path.exists():
        raise FileNotFoundError(f"O diretório {path_file} não existe")
    
    if not path.is_dir():
        raise ValueError(f"O caminho {path_file} não é um diretório")
    
    arquivos = list(Path.glob(path, ref))
    
    if not arquivos:
        raise ValueError(f"Nenhum arquivo encontrado com a referência '{ref}' no diretório {path_file}")
    
    return max(arquivos, key=lambda x: x.stat().st_mtime)
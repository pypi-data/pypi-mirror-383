"""
File Finder Utility

Uma utilitário Python para encontrar e gerenciar arquivos baseado em padrões de nome e data de modificação.
"""

__version__ = "0.0.1"
__author__ = "Pablo Dias"
__email__ = "dias.pabloh@gmail.com"

from .core import check_last_file

__all__ = ["check_last_file"]
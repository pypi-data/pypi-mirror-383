"""
PDF Notes Extractor - Extractor de tablas desde notas en PDFs de estados financieros
"""

__version__ = "0.1.2"
__author__ = "Diego Jiménez"
__email__ = "diego.jimenez.g@gmail.com"

from .core import extract_tables_from_notes
from .models import NoteLocation, ExtractionResult
from .extractors import CamelotExtractor, TabulaExtractor
from .output import OutputManager

__all__ = [
    "extract_tables_from_notes",
    "NoteLocation",
    "ExtractionResult",
    "CamelotExtractor",
    "TabulaExtractor",
    "OutputManager",
]

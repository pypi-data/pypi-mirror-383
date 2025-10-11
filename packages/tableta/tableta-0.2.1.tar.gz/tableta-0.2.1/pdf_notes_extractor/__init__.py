"""
PDF Notes Extractor - Extractor de tablas desde notas en PDFs de estados financieros
Versión mejorada con lógica del playground integrada
"""

__version__ = "0.2.1"
__author__ = "Diego Jiménez"
__email__ = "diego.jimenez.g@gmail.com"

from .core import extract_tables_from_notes
from .models import NoteLocation, ExtractionResult
from .extractors import PDFPlumberExtractor, CamelotExtractor, TabulaExtractor
from .output import OutputManager

__all__ = [
    "extract_tables_from_notes",
    "NoteLocation",
    "ExtractionResult",
    "PDFPlumberExtractor",
    "CamelotExtractor",
    "TabulaExtractor",
    "OutputManager",
]

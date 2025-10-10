"""
Modelos de datos para el extractor de notas PDF
"""

from dataclasses import dataclass, field
from typing import List
import pandas as pd


@dataclass
class NoteLocation:
    """Representa la ubicación de una nota en el PDF"""

    number: int
    start_page: int
    end_page: int
    char_position: int = 0

    def pages_range(self) -> str:
        """
        Retorna el rango de páginas en formato string

        Returns:
            str: Formato "inicio-fin" o "inicio" si es una sola página
        """
        if self.start_page != self.end_page:
            return f"{self.start_page}-{self.end_page}"
        return f"{self.start_page}"


@dataclass
class ExtractionResult:
    """Resultado de la extracción para una nota"""

    note_number: int
    tables: List[pd.DataFrame]
    pages_processed: str
    extraction_time: float
    warnings: List[str] = field(default_factory=list)

    @property
    def has_tables(self) -> bool:
        """Indica si se encontraron tablas"""
        return len(self.tables) > 0

    @property
    def table_count(self) -> int:
        """Número de tablas encontradas"""
        return len(self.tables)

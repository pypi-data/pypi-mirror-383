"""
Patrones de expresiones regulares para detectar notas en PDFs
"""

import re
from typing import List, Tuple


class NotePatterns:
    """Patrones para detectar diferentes formatos de encabezados de notas"""

    # Patrón principal - más flexible para español
    MAIN = re.compile(r"(?mi)^\s*Nota\s*(?:N[º°o\.]*\s*)?(\d{1,3})\b")

    # Patrones alternativos para diferentes idiomas y formatos
    ALTERNATIVES = [
        re.compile(r"(?mi)^\s*Note\s+(\d{1,3})\b"),  # Inglés
        re.compile(r"(?mi)^\s*Anexo\s+(\d{1,3})\b"),  # Anexos
        re.compile(r"(?mi)^\s*\d+\.\s*Nota\s+(\d{1,3})\b"),  # Con numeración previa
    ]

    @classmethod
    def find_all(cls, text: str) -> List[Tuple[int, int]]:
        """
        Encuentra todas las coincidencias de notas en el texto

        Args:
            text: Texto donde buscar las notas

        Returns:
            Lista de tuplas (posición_en_texto, número_de_nota)
        """
        matches = []

        # Buscar con patrón principal
        for m in cls.MAIN.finditer(text):
            matches.append((m.start(), int(m.group(1))))

        # Si no hay matches, probar alternativos
        if not matches:
            for pattern in cls.ALTERNATIVES:
                for m in pattern.finditer(text):
                    matches.append((m.start(), int(m.group(1))))

        return matches

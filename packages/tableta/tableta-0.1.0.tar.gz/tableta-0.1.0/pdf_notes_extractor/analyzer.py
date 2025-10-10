"""
Análisis de estructura de PDFs y búsqueda de notas
"""

import logging
from pathlib import Path
from typing import Dict

import pdfplumber

from .models import NoteLocation
from .patterns import NotePatterns

logger = logging.getLogger(__name__)


def analyze_pdf_structure(pdf_path: Path) -> Dict:
    """
    Analiza la estructura general del PDF

    Args:
        pdf_path: Ruta al archivo PDF

    Returns:
        Diccionario con información sobre el PDF
    """
    info = {
        "total_pages": 0,
        "notes_found": [],
        "has_tables": False,
        "text_extractable": True,
    }

    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            info["total_pages"] = len(pdf.pages)

            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    # Verificar si hay tablas
                    tables = page.extract_tables()
                    if tables:
                        info["has_tables"] = True
                else:
                    info["text_extractable"] = False

    except Exception as e:
        logger.error(f"Error analizando PDF: {e}")

    return info


def find_note_locations(
    pdf_path: Path, verbose: bool = False
) -> Dict[int, NoteLocation]:
    """
    Escanea el PDF y encuentra todas las notas con sus rangos de páginas

    Args:
        pdf_path: Ruta al archivo PDF
        verbose: Si es True, muestra información detallada

    Returns:
        Diccionario {número_nota: NoteLocation}
    """
    all_occurrences = []

    with pdfplumber.open(str(pdf_path)) as pdf:
        total_pages = len(pdf.pages)

        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""

            # Buscar todas las coincidencias en esta página
            matches = NotePatterns.find_all(text)
            for char_pos, note_num in matches:
                all_occurrences.append(
                    NoteLocation(
                        number=note_num,
                        start_page=page_num,
                        end_page=page_num,  # Se actualizará después
                        char_position=char_pos,
                    )
                )

                if verbose:
                    logger.debug(f"Encontrada Nota {note_num} en página {page_num}")

    # Construir rangos de páginas
    locations = {}

    # Agrupar por número de nota y tomar la primera ocurrencia
    for loc in all_occurrences:
        if loc.number not in locations:
            locations[loc.number] = loc

    # Ordenar por página y posición para determinar rangos
    sorted_locs = sorted(
        locations.values(), key=lambda x: (x.start_page, x.char_position)
    )

    # Actualizar end_page para cada nota
    for i, loc in enumerate(sorted_locs):
        if i < len(sorted_locs) - 1:
            next_loc = sorted_locs[i + 1]
            loc.end_page = max(loc.start_page, next_loc.start_page - 1)
        else:
            loc.end_page = total_pages

        locations[loc.number] = loc

    return locations

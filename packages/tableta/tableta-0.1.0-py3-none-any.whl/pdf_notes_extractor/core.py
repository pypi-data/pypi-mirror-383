"""
Funcionalidad principal de extracción de tablas
"""

import time
import logging
from pathlib import Path
from typing import Dict, Set

from .models import ExtractionResult
from .analyzer import analyze_pdf_structure, find_note_locations
from .extractors import CamelotExtractor, TabulaExtractor

logger = logging.getLogger(__name__)


def extract_tables_from_notes(
    pdf_path: Path,
    note_numbers: Set[int],
    engine: str = "camelot",
    verbose: bool = False,
) -> Dict[int, ExtractionResult]:
    """
    Extrae tablas de las notas especificadas del PDF

    Args:
        pdf_path: Ruta al archivo PDF
        note_numbers: Conjunto de números de nota a procesar
        engine: Motor de extracción ('camelot' o 'tabula')
        verbose: Si es True, muestra información detallada

    Returns:
        Diccionario con resultados de extracción por número de nota

    Raises:
        ValueError: Si el engine especificado no es válido
        FileNotFoundError: Si el PDF no existe

    Example:
        >>> from pathlib import Path
        >>> results = extract_tables_from_notes(
        ...     Path('estados_financieros.pdf'),
        ...     {1, 6, 12},
        ...     engine='camelot'
        ... )
        >>> for note_num, result in results.items():
        ...     print(f"Nota {note_num}: {len(result.tables)} tablas")
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"El archivo {pdf_path} no existe")

    if engine not in ["camelot", "tabula"]:
        raise ValueError(f"Engine '{engine}' no válido. Use 'camelot' o 'tabula'")

    results = {}

    # Analizar estructura del PDF
    if verbose:
        logger.info("Analizando estructura del PDF...")
        pdf_info = analyze_pdf_structure(pdf_path)
        logger.info(
            f"PDF: {pdf_info['total_pages']} páginas, "
            f"tablas detectadas: {pdf_info['has_tables']}"
        )

    # Encontrar ubicaciones de las notas
    logger.info("Buscando notas en el documento...")
    locations = find_note_locations(pdf_path, verbose)

    if not locations:
        logger.error("No se encontraron notas en el documento")
        return results

    logger.info(f"Notas encontradas: {sorted(locations.keys())}")

    # Verificar notas solicitadas
    missing_notes = note_numbers - set(locations.keys())
    if missing_notes:
        logger.warning(
            f"Notas solicitadas pero no encontradas: {sorted(missing_notes)}"
        )

    # Seleccionar extractor
    try:
        if engine == "camelot":
            extractor = CamelotExtractor()
        else:
            extractor = TabulaExtractor()
    except RuntimeError as e:
        logger.error(str(e))
        raise

    # Procesar cada nota
    for note_num in sorted(note_numbers):
        if note_num not in locations:
            # Agregar resultado vacío para notas no encontradas
            results[note_num] = ExtractionResult(
                note_number=note_num,
                tables=[],
                pages_processed="N/A",
                extraction_time=0,
                warnings=["Nota no encontrada en el documento"],
            )
            continue

        location = locations[note_num]
        logger.info(
            f"\nProcesando Nota {note_num} (páginas {location.pages_range()})..."
        )

        start_time = time.time()
        warnings = []

        try:
            tables = extractor.extract(pdf_path, location.pages_range())

            if not tables:
                warnings.append("No se encontraron tablas en esta nota")
            else:
                logger.info(f"Nota {note_num}: {len(tables)} tabla(s) extraída(s)")

                # Validación básica de las tablas
                for i, df in enumerate(tables, 1):
                    if df.shape[0] < 2:
                        warnings.append(
                            f"Tabla {i} tiene muy pocas filas ({df.shape[0]})"
                        )
                    if df.shape[1] < 2:
                        warnings.append(
                            f"Tabla {i} tiene muy pocas columnas ({df.shape[1]})"
                        )

        except Exception as e:
            logger.error(f"Error procesando Nota {note_num}: {e}")
            tables = []
            warnings.append(f"Error en extracción: {str(e)}")

        extraction_time = time.time() - start_time

        results[note_num] = ExtractionResult(
            note_number=note_num,
            tables=tables,
            pages_processed=location.pages_range(),
            extraction_time=extraction_time,
            warnings=warnings,
        )

    return results

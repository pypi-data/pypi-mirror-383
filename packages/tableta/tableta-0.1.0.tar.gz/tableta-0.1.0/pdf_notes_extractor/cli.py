#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI para el extractor de tablas de notas PDF
"""

import sys
import argparse
import logging
from pathlib import Path

from . import __version__
from .core import extract_tables_from_notes
from .analyzer import find_note_locations
from .output import OutputManager

# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Punto de entrada principal del CLI"""
    parser = argparse.ArgumentParser(
        description="Extractor de tablas desde Notas en PDFs de Estados Financieros",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s documento.pdf --notas 1 6 12 --excel resultado.xlsx
  %(prog)s documento.pdf --notas 1 6 --csv-dir ./tablas --engine tabula
  %(prog)s documento.pdf --notas all --excel todo.xlsx --verbose
  %(prog)s documento.pdf --notas 1-5 --excel resultado.xlsx
        """,
    )

    parser.add_argument("pdf", type=Path, help="Ruta al archivo PDF")
    parser.add_argument(
        "--notas",
        nargs="+",
        required=True,
        help='Números de nota a extraer (ej: 1 6 12, o "all" para todas, o "1-5" para rango)',
    )
    parser.add_argument(
        "--engine",
        choices=["camelot", "tabula"],
        default="camelot",
        help="Motor de extracción (default: camelot)",
    )
    parser.add_argument("--excel", type=Path, help="Guardar resultado en Excel")
    parser.add_argument("--csv-dir", type=Path, help="Guardar CSVs en carpeta")
    parser.add_argument("--metadata", type=Path, help="Guardar metadatos JSON")
    parser.add_argument(
        "--verbose", action="store_true", help="Mostrar información detallada"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Mostrar mensajes de depuración"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()

    # Configurar logging
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger("pdf_notes_extractor").setLevel(logging.DEBUG)
    elif not args.verbose:
        logger.setLevel(logging.WARNING)

    # Validar entrada
    if not args.pdf.exists():
        logger.error(f"El archivo {args.pdf} no existe")
        sys.exit(1)

    if not args.excel and not args.csv_dir:
        logger.error(
            "Debes especificar --excel y/o --csv-dir para guardar los resultados"
        )
        sys.exit(1)

    # Procesar números de nota
    note_numbers = parse_note_numbers(args.notas, args.pdf, args.verbose)

    if not note_numbers:
        logger.error("No se especificaron notas válidas")
        sys.exit(1)

    # Extraer tablas
    logger.info(f"Iniciando extracción con motor '{args.engine}'...")
    try:
        results = extract_tables_from_notes(
            args.pdf, note_numbers, engine=args.engine, verbose=args.verbose
        )
    except Exception as e:
        logger.error(f"Error durante la extracción: {e}")
        sys.exit(1)

    if not results:
        logger.error("No se pudo extraer ninguna tabla")
        sys.exit(1)

    # Guardar resultados
    output_manager = OutputManager()

    if args.excel:
        output_manager.save_to_excel(results, args.excel)

    if args.csv_dir:
        output_manager.save_to_csv(results, args.csv_dir)

    if args.metadata:
        locations = find_note_locations(args.pdf, False)
        output_manager.save_metadata(results, locations, args.metadata)

    # Resumen final
    print_summary(results, args)


def parse_note_numbers(notas_arg, pdf_path, verbose):
    """
    Parsea los argumentos de notas y retorna un conjunto de números

    Args:
        notas_arg: Lista de strings con números o "all" o rangos
        pdf_path: Ruta al PDF (para obtener todas las notas si se usa "all")
        verbose: Flag de verbosidad

    Returns:
        Set de números de nota
    """
    note_numbers = set()

    if notas_arg == ["all"]:
        # Encontrar todas las notas
        locations = find_note_locations(pdf_path, verbose)
        note_numbers = set(locations.keys())
        logger.info(
            f"Modo 'all': procesando todas las notas encontradas: {sorted(note_numbers)}"
        )
    else:
        for item in notas_arg:
            # Verificar si es un rango (ej: "1-5")
            if "-" in item:
                try:
                    start, end = map(int, item.split("-"))
                    note_numbers.update(range(start, end + 1))
                except ValueError:
                    logger.warning(f"Rango inválido: {item}")
            else:
                # Número individual
                try:
                    note_numbers.add(int(item))
                except ValueError:
                    logger.warning(f"Número de nota inválido: {item}")

    return note_numbers


def print_summary(results, args):
    """Imprime un resumen de los resultados"""
    total_tables = sum(len(r.tables) for r in results.values())

    print(f"\n{'='*50}")
    print(f"Extracción completada:")
    print(f"  - Notas procesadas: {len(results)}")
    print(f"  - Total de tablas extraídas: {total_tables}")

    if args.excel:
        print(f"  - Resultado Excel: {args.excel}")
    if args.csv_dir:
        print(f"  - Resultados CSV: {args.csv_dir}")
    if args.metadata:
        print(f"  - Metadatos: {args.metadata}")


if __name__ == "__main__":
    main()

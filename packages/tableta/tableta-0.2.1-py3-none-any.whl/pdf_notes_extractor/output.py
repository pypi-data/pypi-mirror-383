"""
Manejo de salida de resultados (Excel, CSV, JSON)
"""

import json
import logging
from pathlib import Path
from typing import Dict
from datetime import datetime

import pandas as pd

from .models import ExtractionResult, NoteLocation

logger = logging.getLogger(__name__)


class OutputManager:
    """Gestiona la salida de resultados en diferentes formatos"""

    @staticmethod
    def save_to_excel(results: Dict[int, ExtractionResult], output_path: Path):
        """
        Guarda resultados en un archivo Excel con múltiples hojas

        Args:
            results: Diccionario de resultados por número de nota
            output_path: Ruta del archivo Excel de salida
        """
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            # Hoja de resumen
            summary_data = []
            for note_num, result in sorted(results.items()):
                summary_data.append(
                    {
                        "Nota": note_num,
                        "Tablas Encontradas": len(result.tables),
                        "Páginas Procesadas": result.pages_processed,
                        "Tiempo (s)": f"{result.extraction_time:.2f}",
                        "Advertencias": ", ".join(result.warnings)
                        if result.warnings
                        else "Ninguna",
                    }
                )

            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name="Resumen", index=False)

            # Una hoja por cada tabla encontrada
            for note_num, result in sorted(results.items()):
                if not result.tables:
                    # Crear hoja vacía para notas sin tablas
                    pd.DataFrame(
                        {"Mensaje": ["No se encontraron tablas en esta nota"]}
                    ).to_excel(
                        writer,
                        sheet_name=f"Nota_{note_num}_sin_tablas"[:31],
                        index=False,
                    )
                else:
                    for idx, df in enumerate(result.tables, start=1):
                        sheet_name = f"Nota_{note_num}_Tabla_{idx}"[:31]
                        df.to_excel(writer, sheet_name=sheet_name, index=False)

                        # Ajustar anchos de columna
                        worksheet = writer.sheets[sheet_name]
                        for column in worksheet.columns:
                            max_length = 0
                            column_letter = column[0].column_letter
                            for cell in column:
                                try:
                                    if len(str(cell.value)) > max_length:
                                        max_length = len(str(cell.value))
                                except:
                                    pass
                            adjusted_width = min(max_length + 2, 50)
                            worksheet.column_dimensions[
                                column_letter
                            ].width = adjusted_width

        logger.info(f"Excel guardado en: {output_path}")

    @staticmethod
    def save_to_csv(results: Dict[int, ExtractionResult], output_dir: Path):
        """
        Guarda resultados como archivos CSV individuales

        Args:
            results: Diccionario de resultados por número de nota
            output_dir: Directorio donde guardar los CSVs
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Guardar resumen
        summary_data = []
        for note_num, result in sorted(results.items()):
            summary_data.append(
                {
                    "Nota": note_num,
                    "Tablas_Encontradas": len(result.tables),
                    "Páginas_Procesadas": result.pages_processed,
                    "Tiempo_segundos": result.extraction_time,
                    "Advertencias": "|".join(result.warnings)
                    if result.warnings
                    else "",
                }
            )

        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(output_dir / "_resumen.csv", index=False, encoding="utf-8")

        # Guardar cada tabla
        for note_num, result in sorted(results.items()):
            if not result.tables:
                # Crear archivo marcador para notas sin tablas
                marker_file = output_dir / f"Nota_{note_num}_sin_tablas.txt"
                marker_file.write_text(
                    "No se encontraron tablas en esta nota", encoding="utf-8"
                )
            else:
                for idx, df in enumerate(result.tables, start=1):
                    csv_path = output_dir / f"Nota_{note_num}_tabla_{idx}.csv"
                    df.to_csv(csv_path, index=False, encoding="utf-8")

        logger.info(f"CSVs guardados en: {output_dir}")

    @staticmethod
    def save_metadata(
        results: Dict[int, ExtractionResult],
        locations: Dict[int, NoteLocation],
        output_path: Path,
    ):
        """
        Guarda metadatos de la extracción en formato JSON

        Args:
            results: Diccionario de resultados por número de nota
            locations: Ubicaciones de las notas en el PDF
            output_path: Ruta del archivo JSON de salida
        """
        metadata = {
            "extraction_date": datetime.now().isoformat(),
            "notes_processed": list(results.keys()),
            "total_tables_found": sum(len(r.tables) for r in results.values()),
            "details": {},
        }

        for note_num, result in results.items():
            location = locations.get(note_num)
            metadata["details"][str(note_num)] = {
                "pages": location.pages_range() if location else "N/A",
                "tables_count": len(result.tables),
                "extraction_time": result.extraction_time,
                "warnings": result.warnings,
                "table_shapes": [list(df.shape) for df in result.tables],
            }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        logger.info(f"Metadatos guardados en: {output_path}")

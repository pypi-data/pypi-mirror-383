#!/usr/bin/env python3
"""
Ejemplo básico de uso de pdf-notes-extractor
"""

from pathlib import Path
from pdf_notes_extractor import extract_tables_from_notes
from pdf_notes_extractor.output import OutputManager


def main():
    # Configuración
    pdf_path = Path("tu_documento.pdf")  # Cambia esto por tu PDF
    note_numbers = {1, 6, 12}  # Notas que quieres extraer
    
    print(f"Extrayendo tablas de las notas {note_numbers}...")
    print(f"Archivo: {pdf_path}\n")
    
    # Extraer tablas
    results = extract_tables_from_notes(
        pdf_path=pdf_path,
        note_numbers=note_numbers,
        engine='camelot',  # o 'tabula'
        verbose=True
    )
    
    # Mostrar resultados
    print("\n" + "="*50)
    print("RESULTADOS:")
    print("="*50)
    
    for note_num, result in sorted(results.items()):
        print(f"\nNota {note_num}:")
        print(f"  ✓ Páginas procesadas: {result.pages_processed}")
        print(f"  ✓ Tablas encontradas: {len(result.tables)}")
        print(f"  ✓ Tiempo de extracción: {result.extraction_time:.2f}s")
        
        if result.warnings:
            print(f"  ⚠ Advertencias:")
            for warning in result.warnings:
                print(f"    - {warning}")
        
        # Mostrar información de cada tabla
        for i, df in enumerate(result.tables, 1):
            print(f"  📊 Tabla {i}:")
            print(f"    - Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
            print(f"    - Primeras filas:")
            print(df.head(3).to_string(index=False))
    
    # Guardar a Excel
    output_path = Path("resultados_extraccion.xlsx")
    output_manager = OutputManager()
    output_manager.save_to_excel(results, output_path)
    
    print(f"\n✅ Resultados guardados en: {output_path}")


if __name__ == "__main__":
    main()

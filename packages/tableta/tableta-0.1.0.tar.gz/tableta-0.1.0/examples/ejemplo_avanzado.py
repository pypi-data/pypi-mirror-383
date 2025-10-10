#!/usr/bin/env python3
"""
Ejemplo avanzado con análisis previo y procesamiento personalizado
"""

from pathlib import Path
from pdf_notes_extractor import extract_tables_from_notes
from pdf_notes_extractor.analyzer import find_note_locations, analyze_pdf_structure
from pdf_notes_extractor.output import OutputManager
import pandas as pd


def main():
    pdf_path = Path("tu_documento.pdf")
    
    print("="*60)
    print("ANÁLISIS PREVIO DEL PDF")
    print("="*60)
    
    # 1. Analizar estructura general
    print("\n1. Analizando estructura del PDF...")
    pdf_info = analyze_pdf_structure(pdf_path)
    print(f"   Total de páginas: {pdf_info['total_pages']}")
    print(f"   Contiene tablas: {'Sí' if pdf_info['has_tables'] else 'No'}")
    print(f"   Texto extraíble: {'Sí' if pdf_info['text_extractable'] else 'No'}")
    
    # 2. Encontrar todas las notas disponibles
    print("\n2. Buscando notas en el documento...")
    locations = find_note_locations(pdf_path, verbose=True)
    
    if not locations:
        print("   ⚠ No se encontraron notas en el documento")
        return
    
    print(f"   ✓ Notas encontradas: {sorted(locations.keys())}")
    print("\n   Detalle de ubicaciones:")
    for note_num, location in sorted(locations.items()):
        print(f"   - Nota {note_num}: páginas {location.pages_range()}")
    
    # 3. Extraer notas específicas
    print("\n" + "="*60)
    print("EXTRACCIÓN DE TABLAS")
    print("="*60)
    
    # Seleccionar algunas notas (por ejemplo, las primeras 3)
    notes_to_extract = set(sorted(locations.keys())[:3])
    print(f"\nExtrayendo notas: {sorted(notes_to_extract)}")
    
    results = extract_tables_from_notes(
        pdf_path=pdf_path,
        note_numbers=notes_to_extract,
        engine='camelot',
        verbose=True
    )
    
    # 4. Procesamiento personalizado de resultados
    print("\n" + "="*60)
    print("PROCESAMIENTO DE RESULTADOS")
    print("="*60)
    
    all_dataframes = []
    
    for note_num, result in sorted(results.items()):
        if not result.tables:
            print(f"\nNota {note_num}: Sin tablas")
            continue
        
        print(f"\nNota {note_num}: {len(result.tables)} tabla(s)")
        
        for i, df in enumerate(result.tables, 1):
            # Agregar metadatos al DataFrame
            df_copy = df.copy()
            df_copy['_nota'] = note_num
            df_copy['_tabla'] = i
            df_copy['_paginas'] = result.pages_processed
            
            all_dataframes.append(df_copy)
            
            # Análisis básico
            print(f"  Tabla {i}:")
            print(f"    - Shape: {df.shape}")
            print(f"    - Columnas: {list(df.columns)}")
            
            # Detectar columnas numéricas
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
            if len(numeric_cols) > 0:
                print(f"    - Columnas numéricas: {len(numeric_cols)}")
    
    # 5. Combinar todas las tablas en un solo DataFrame
    if all_dataframes:
        print("\n5. Consolidando todas las tablas...")
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        print(f"   ✓ DataFrame consolidado: {combined_df.shape}")
        
        # Guardar consolidado
        consolidated_path = Path("tablas_consolidadas.csv")
        combined_df.to_csv(consolidated_path, index=False, encoding='utf-8')
        print(f"   ✓ Guardado en: {consolidated_path}")
    
    # 6. Guardar resultados
    print("\n6. Guardando resultados...")
    output_manager = OutputManager()
    
    # Excel
    excel_path = Path("resultados_completos.xlsx")
    output_manager.save_to_excel(results, excel_path)
    print(f"   ✓ Excel: {excel_path}")
    
    # CSV individuales
    csv_dir = Path("tablas_csv")
    output_manager.save_to_csv(results, csv_dir)
    print(f"   ✓ CSVs: {csv_dir}/")
    
    # Metadatos
    metadata_path = Path("metadatos.json")
    output_manager.save_metadata(results, locations, metadata_path)
    print(f"   ✓ Metadatos: {metadata_path}")
    
    print("\n" + "="*60)
    print("✅ PROCESO COMPLETADO")
    print("="*60)


if __name__ == "__main__":
    main()

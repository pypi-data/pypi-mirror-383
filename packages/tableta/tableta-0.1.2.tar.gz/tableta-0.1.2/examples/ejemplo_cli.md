# Ejemplos de uso desde línea de comandos

## Casos de uso básicos

### 1. Extraer notas específicas a Excel
```bash
pdf-notes-extractor documento.pdf --notas 1 6 12 --excel resultado.xlsx
```

### 2. Extraer todas las notas
```bash
pdf-notes-extractor documento.pdf --notas all --excel todas_las_notas.xlsx
```

### 3. Extraer un rango de notas
```bash
pdf-notes-extractor documento.pdf --notas 1-10 --excel notas_1_a_10.xlsx
```

### 4. Combinar números individuales y rangos
```bash
pdf-notes-extractor documento.pdf --notas 1 3 5-8 12 --excel resultado.xlsx
```

## Exportar a diferentes formatos

### 5. Exportar solo a CSV
```bash
pdf-notes-extractor documento.pdf --notas 1 6 --csv-dir ./tablas_csv
```

### 6. Exportar a Excel y CSV simultáneamente
```bash
pdf-notes-extractor documento.pdf --notas 1 6 --excel resultado.xlsx --csv-dir ./csv
```

### 7. Incluir archivo de metadatos JSON
```bash
pdf-notes-extractor documento.pdf --notas 1 6 --excel resultado.xlsx --metadata metadatos.json
```

## Usar diferentes motores de extracción

### 8. Usar Tabula en lugar de Camelot
```bash
pdf-notes-extractor documento.pdf --notas 1 6 --excel resultado.xlsx --engine tabula
```

### 9. Usar Camelot (por defecto)
```bash
pdf-notes-extractor documento.pdf --notas 1 6 --excel resultado.xlsx --engine camelot
```

## Opciones de verbosidad

### 10. Modo verbose (información detallada)
```bash
pdf-notes-extractor documento.pdf --notas 1 6 --excel resultado.xlsx --verbose
```

### 11. Modo debug (máxima información)
```bash
pdf-notes-extractor documento.pdf --notas 1 6 --excel resultado.xlsx --debug
```

### 12. Modo silencioso (solo errores)
```bash
pdf-notes-extractor documento.pdf --notas 1 6 --excel resultado.xlsx
```

## Casos de uso avanzados

### 13. Procesamiento batch de múltiples PDFs
```bash
for pdf in *.pdf; do
    pdf-notes-extractor "$pdf" --notas all --excel "${pdf%.pdf}_tablas.xlsx"
done
```

### 14. Extraer y comprimir resultados
```bash
pdf-notes-extractor documento.pdf --notas all --csv-dir ./tablas
zip -r tablas.zip ./tablas
```

### 15. Pipeline completo con validación
```bash
# Verificar que el PDF existe
if [ -f "documento.pdf" ]; then
    # Extraer con metadatos
    pdf-notes-extractor documento.pdf \
        --notas 1 6 12 \
        --excel resultado.xlsx \
        --csv-dir ./csv \
        --metadata meta.json \
        --verbose
    
    # Verificar que se generaron los archivos
    if [ -f "resultado.xlsx" ]; then
        echo "✅ Extracción exitosa"
    else
        echo "❌ Error en la extracción"
    fi
else
    echo "❌ PDF no encontrado"
fi
```

## Ejemplos específicos para estados financieros

### 16. Extraer notas contables típicas
```bash
# Notas de políticas contables, activos, pasivos
pdf-notes-extractor eeff_2024.pdf --notas 2 5 6 7 8 --excel politicas_y_balances.xlsx
```

### 17. Extraer solo notas de revelación
```bash
pdf-notes-extractor eeff_2024.pdf --notas 10-20 --excel revelaciones.xlsx --verbose
```

### 18. Extraer y validar notas de instrumentos financieros
```bash
pdf-notes-extractor eeff_2024.pdf \
    --notas 7 8 9 \
    --excel instrumentos_financieros.xlsx \
    --csv-dir ./instrumentos_csv \
    --metadata validacion.json \
    --verbose
```

## Troubleshooting

### 19. Ver versión instalada
```bash
pdf-notes-extractor --version
```

### 20. Ver ayuda completa
```bash
pdf-notes-extractor --help
```

### 21. Test rápido con debug
```bash
pdf-notes-extractor test.pdf --notas 1 --excel test.xlsx --debug
```

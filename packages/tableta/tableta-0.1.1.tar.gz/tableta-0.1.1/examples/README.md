# Ejemplos de Uso

Esta carpeta contiene ejemplos prácticos de cómo usar `pdf-notes-extractor`.

## 📁 Archivos

### 1. `ejemplo_basico.py`
Ejemplo simple que muestra:
- Extracción de notas específicas
- Visualización de resultados
- Guardado a Excel

**Ejecutar:**
```bash
python ejemplo_basico.py
```

### 2. `ejemplo_avanzado.py`
Ejemplo completo que muestra:
- Análisis previo del PDF
- Búsqueda de todas las notas
- Procesamiento personalizado de DataFrames
- Consolidación de tablas
- Múltiples formatos de salida

**Ejecutar:**
```bash
python ejemplo_avanzado.py
```

### 3. `ejemplo_cli.md`
Guía completa de uso desde línea de comandos con:
- Casos de uso básicos
- Casos de uso avanzados
- Scripts de ejemplo
- Troubleshooting

## 🚀 Antes de Ejecutar

1. Asegúrate de tener un PDF de prueba
2. Modifica la variable `pdf_path` en los scripts
3. Instala las dependencias necesarias:

```bash
pip install pdf-notes-extractor[camelot]
```

## 💡 Adaptando los Ejemplos

### Para tus propios PDFs

Simplemente cambia:

```python
pdf_path = Path("tu_documento.pdf")  # Tu PDF
note_numbers = {1, 6, 12}  # Tus notas
```

### Para descubrir qué notas tienes

```python
from pdf_notes_extractor.analyzer import find_note_locations

locations = find_note_locations(Path("tu_documento.pdf"))
print(f"Notas disponibles: {sorted(locations.keys())}")
```

## 📊 Qué Esperar

Los ejemplos generarán:
- `resultado.xlsx` o `resultados_completos.xlsx` - Archivo Excel con todas las tablas
- `tablas_csv/` - Carpeta con CSVs individuales
- `metadatos.json` - Información sobre la extracción
- `tablas_consolidadas.csv` - Todas las tablas en un solo archivo

## 🐛 Troubleshooting

### No encuentra el PDF
```python
pdf_path = Path("ruta/completa/a/tu/documento.pdf")
```

### No extrae tablas
- Prueba con `engine='tabula'` en lugar de `'camelot'`
- Verifica que el PDF no sea escaneado (debe tener texto seleccionable)
- Usa `verbose=True` para ver más detalles

### Error de dependencias
```bash
pip install pdf-notes-extractor[all]
```

## 🔗 Más Información

- [README principal](../README.md)
- [Guía de inicio rápido](../QUICKSTART.md)
- [Documentación de la API](../README.md#-uso)

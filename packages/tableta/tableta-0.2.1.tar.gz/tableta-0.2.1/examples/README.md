# Ejemplos de Uso

Esta carpeta contiene ejemplos prácticos de cómo usar `pdf-notes-extractor`.

## 🎯 Versión 0.2.0 - Actualizada

Los ejemplos han sido actualizados para usar el motor **pdfplumber** por defecto, que ofrece:
- Mayor precisión en la detección de notas
- Mejor extracción de tablas (73% menos falsos positivos)
- No requiere dependencias adicionales

## 📁 Archivos

### 1. `ejemplo_basico.py`
Ejemplo simple que muestra:
- Extracción de notas específicas usando pdfplumber
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
# Instalación básica (incluye pdfplumber - recomendado)
pip install tableta

# O con motores adicionales (opcional)
pip install tableta[all]
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
- El motor por defecto es `pdfplumber` (recomendado)
- Si no funciona, prueba con `engine='camelot'` o `engine='tabula'`
- Verifica que el PDF no sea escaneado (debe tener texto seleccionable)
- Usa `verbose=True` para ver más detalles

### Error de dependencias
```bash
# Instalar con todos los motores
pip install tableta[all]
```

### Muchos falsos positivos
- La versión 0.2.0 ya reduce ~73% de falsos positivos con pdfplumber
- Asegúrate de estar usando `engine='pdfplumber'` (es el predeterminado)

## 🔗 Más Información

- [README principal](../README.md)
- [Guía de inicio rápido](../QUICKSTART.md)
- [Documentación de la API](../README.md#-uso)

# PDF Notes Extractor

Librería Python para extraer tablas desde notas en PDFs de estados financieros.

## 📋 Características

- ✅ Extrae tablas de notas específicas en PDFs
- ✅ Soporta múltiples motores de extracción (Camelot, Tabula)
- ✅ Exporta a Excel con múltiples hojas
- ✅ Exporta a CSV individuales
- ✅ Interfaz de línea de comandos (CLI)
- ✅ API programática para usar en scripts
- ✅ Detección automática de rangos de páginas por nota
- ✅ Limpieza y normalización de datos

## 🚀 Instalación

### Instalación básica (solo pdfplumber)

```bash
pip install tableta
```

### Con soporte para Camelot (recomendado)

```bash
pip install tableta[camelot]
```

### Con soporte para Tabula

```bash
pip install tableta[tabula]
```

### Con todos los extractores

```bash
pip install tableta[all]
```

### Para desarrollo

```bash
git clone https://github.com/diegonov1/tableta.git
cd tableta
pip install -e ".[dev]"
```

## 💻 Uso

### Línea de comandos (CLI)

#### Extraer notas específicas a Excel

```bash
tableta documento.pdf --notas 1 6 12 --excel resultado.xlsx
```

#### Extraer todas las notas

```bash
tableta documento.pdf --notas all --excel resultado.xlsx
```

#### Extraer rango de notas

```bash
tableta documento.pdf --notas 1-5 --excel resultado.xlsx
```

#### Exportar a CSV

```bash
tableta documento.pdf --notas 1 6 --csv-dir ./tablas
```

#### Usar motor Tabula

```bash
tableta documento.pdf --notas 1 6 --excel resultado.xlsx --engine tabula
```

#### Con información detallada

```bash
tableta documento.pdf --notas 1 6 --excel resultado.xlsx --verbose
```

#### Guardar metadatos

```bash
tableta documento.pdf --notas 1 6 --excel resultado.xlsx --metadata meta.json
```

### API Programática

```python
from pathlib import Path
from pdf_notes_extractor import extract_tables_from_notes
from pdf_notes_extractor.output import OutputManager

# Extraer tablas de las notas 1, 6 y 12
pdf_path = Path("estados_financieros.pdf")
note_numbers = {1, 6, 12}

results = extract_tables_from_notes(
    pdf_path=pdf_path,
    note_numbers=note_numbers,
    engine='camelot',
    verbose=True
)

# Procesar resultados
for note_num, result in results.items():
    print(f"Nota {note_num}:")
    print(f"  - Tablas encontradas: {len(result.tables)}")
    print(f"  - Páginas: {result.pages_processed}")
    print(f"  - Tiempo: {result.extraction_time:.2f}s")
    
    # Acceder a las tablas (pandas DataFrames)
    for i, df in enumerate(result.tables, 1):
        print(f"  - Tabla {i}: {df.shape[0]} filas x {df.shape[1]} columnas")

# Guardar a Excel
output_manager = OutputManager()
output_manager.save_to_excel(results, Path("resultado.xlsx"))
```

### Uso avanzado

```python
from pdf_notes_extractor import extract_tables_from_notes
from pdf_notes_extractor.analyzer import find_note_locations, analyze_pdf_structure
from pdf_notes_extractor.extractors import CamelotExtractor
from pathlib import Path

pdf_path = Path("documento.pdf")

# Analizar estructura del PDF
pdf_info = analyze_pdf_structure(pdf_path)
print(f"Total páginas: {pdf_info['total_pages']}")
print(f"Tiene tablas: {pdf_info['has_tables']}")

# Encontrar todas las notas disponibles
locations = find_note_locations(pdf_path)
print(f"Notas encontradas: {sorted(locations.keys())}")

for note_num, location in locations.items():
    print(f"Nota {note_num}: páginas {location.pages_range()}")

# Usar extractor específico
extractor = CamelotExtractor()
tables = extractor.extract(pdf_path, pages="1-5")
```

## 📖 Estructura del Proyecto

```
tableta/
├── pdf_notes_extractor/
│   ├── __init__.py          # API pública
│   ├── cli.py               # Interfaz de línea de comandos
│   ├── core.py              # Función principal de extracción
│   ├── models.py            # Modelos de datos
│   ├── patterns.py          # Patrones regex para detectar notas
│   ├── analyzer.py          # Análisis de PDFs
│   ├── extractors.py        # Extractores (Camelot, Tabula)
│   └── output.py            # Exportación de resultados
├── tests/                   # Tests unitarios
├── examples/                # Ejemplos de uso
├── pyproject.toml           # Configuración del proyecto
├── setup.py                 # Setup alternativo
├── README.md                # Este archivo
├── LICENSE                  # Licencia MIT
└── .gitignore              # Archivos a ignorar
```

## 🔧 Requisitos

- Python >= 3.8
- pandas >= 1.3.0
- pdfplumber >= 0.7.0
- openpyxl >= 3.0.0

### Opcionales

- camelot-py[cv] >= 0.11.0 (para mejor extracción de tablas)
- tabula-py >= 2.5.0 (motor alternativo)

## 📝 Formato de Salida

### Excel

El archivo Excel generado contiene:
- **Hoja "Resumen"**: Información general de todas las notas procesadas
- **Hojas individuales**: Una hoja por cada tabla encontrada (formato: `Nota_X_Tabla_Y`)

### CSV

Genera archivos individuales:
- `_resumen.csv`: Resumen de la extracción
- `Nota_X_tabla_Y.csv`: Cada tabla en su propio archivo
- `Nota_X_sin_tablas.txt`: Marcador para notas sin tablas

### JSON (Metadatos)

```json
{
  "extraction_date": "2025-10-10T01:43:11",
  "notes_processed": [1, 6, 12],
  "total_tables_found": 5,
  "details": {
    "1": {
      "pages": "10-12",
      "tables_count": 2,
      "extraction_time": 1.23,
      "warnings": [],
      "table_shapes": [[10, 5], [15, 4]]
    }
  }
}
```

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🐛 Reportar Problemas

Si encuentras algún problema, por favor abre un issue en GitHub incluyendo:
- Descripción del problema
- Pasos para reproducirlo
- Versión de Python y librerías
- Ejemplo de PDF (si es posible)

## 🙏 Agradecimientos

Esta librería utiliza las siguientes herramientas:
- [pdfplumber](https://github.com/jsvine/pdfplumber) - Extracción de texto y tablas
- [Camelot](https://github.com/camelot-dev/camelot) - Extracción avanzada de tablas
- [Tabula](https://github.com/tabulapdf/tabula-py) - Motor alternativo de extracción
- [pandas](https://pandas.pydata.org/) - Manipulación de datos

## 📊 Estado del Proyecto

- ✅ Versión Beta (0.1.0)
- 🚧 En desarrollo activo
- 📝 Documentación en progreso

## 🗺️ Roadmap

- [ ] Soporte para más idiomas en detección de notas
- [ ] Interfaz gráfica (GUI)
- [ ] Exportación a más formatos (JSON, SQLite)
- [ ] Mejor detección de tablas complejas
- [ ] Caché de resultados
- [ ] Procesamiento en paralelo de múltiples notas

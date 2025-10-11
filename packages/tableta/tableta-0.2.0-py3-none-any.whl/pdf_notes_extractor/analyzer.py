"""
Análisis de estructura de PDFs y búsqueda de notas
Integrado con la lógica mejorada del playground
"""

import logging
import re
from pathlib import Path
from typing import Dict, List

import pdfplumber

from .models import NoteLocation

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


def is_subtitle(line: str, prev_line: str = "", next_line: str = "") -> bool:
    """
    Determina si una línea que contiene 'NOTA X' es un subtítulo o no.
    
    Criterios para subtítulo (basado en playground):
    1. NO debe terminar con un número de página (excluir tabla de contenidos)
    2. Debe ser relativamente corta (los subtítulos son concisos)
    3. NO debe contener "CONTINUACIÓN" (queremos solo la primera ocurrencia)
    4. NO debe contener palabras comunes en texto del cuerpo
    
    Args:
        line: La línea a verificar
        prev_line: Línea anterior para contexto
        next_line: Línea siguiente para contexto
        
    Returns:
        True si la línea es un subtítulo, False en caso contrario
    """
    # Remover espacios en blanco al inicio y final
    line = line.strip()
    
    # Excluir continuaciones - solo queremos la primera ocurrencia
    if "CONTINUACIÓN" in line.upper() or "CONTINUACION" in line.upper():
        return False
    
    # Verificar si la línea termina con un número de página (patrón de tabla de contenidos)
    # Patrón: termina con 1-3 dígitos, posiblemente con espacios
    if re.search(r'\d{1,3}\s*$', line):
        return False
    
    # Excluir líneas demasiado largas (probablemente parte del texto del cuerpo)
    # Los subtítulos suelen ser concisos (menos de 100 caracteres)
    if len(line) > 100:
        return False
    
    # Excluir líneas con indicadores comunes de texto del cuerpo
    body_text_indicators = ['tabla', 'siguiente', 'detalle', 'incluye', 'total']
    line_lower = line.lower()
    for indicator in body_text_indicators:
        if indicator in line_lower:
            return False
    
    # Verificar si la línea anterior indica que estamos en la sección de notas
    # Esto ayuda a confirmar que es un subtítulo
    if prev_line and "Notas a los Estados Financieros" in prev_line:
        return True
    
    # Verificación adicional: si la línea anterior tiene un patrón de fecha (común en encabezados)
    if prev_line and re.search(r'\d{2}\s+de\s+\w+\s+de\s+\d{4}', prev_line):
        return True
    
    # Si ninguno de los criterios de exclusión coincidió, probablemente es un subtítulo
    return True


def find_note_locations(
    pdf_path: Path, verbose: bool = False
) -> Dict[int, NoteLocation]:
    """
    Escanea el PDF y encuentra todas las notas con sus rangos de páginas.
    Usa la lógica mejorada del playground para detectar subtítulos correctamente.

    Args:
        pdf_path: Ruta al archivo PDF
        verbose: Si es True, muestra información detallada

    Returns:
        Diccionario {número_nota: NoteLocation}
    """
    results = {}
    
    with pdfplumber.open(str(pdf_path)) as pdf:
        total_pages = len(pdf.pages)

        # Iterar por todas las páginas
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            text = page.extract_text()
            
            if not text:
                continue
            
            lines = text.split('\n')
            
            # Verificar cada línea en busca de patrones de nota
            for i, line in enumerate(lines):
                # Patrón: "NOTA" seguido de espacio en blanco y el número de nota
                # Usar límite de palabra para evitar coincidir NOTA 60 cuando buscamos NOTA 6
                # También asegurar que no esté seguido por un punto (para evitar "Nota 2.30")
                pattern = r'\bNOTA\s+(\d{1,3})(?!\.)(?=\s|$|[A-Z])'
                
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    note_num = int(match.group(1))
                    
                    # Obtener líneas de contexto
                    prev_line = lines[i-1] if i > 0 else ""
                    next_line = lines[i+1] if i < len(lines) - 1 else ""
                    
                    # Verificar si esto es un subtítulo
                    if is_subtitle(line, prev_line, next_line):
                        # Solo registrar si aún no hemos encontrado esta nota
                        # (para obtener solo la primera ocurrencia)
                        if note_num not in results:
                            results[note_num] = NoteLocation(
                                number=note_num,
                                start_page=page_num + 1,  # 1-indexed
                                end_page=page_num + 1,    # Se actualizará después
                                char_position=0
                            )
                            
                            if verbose:
                                logger.info(f"Encontrada NOTA {note_num} en página {page_num + 1}")

        # Determinar rangos de páginas
        # Necesitamos encontrar también las notas siguientes para definir los rangos
        all_note_numbers = sorted(results.keys())
        
        for i, note_num in enumerate(all_note_numbers):
            location = results[note_num]
            
            # El rango va desde el inicio de esta nota hasta el inicio de la siguiente nota - 1
            if i < len(all_note_numbers) - 1:
                next_note_num = all_note_numbers[i + 1]
                next_location = results[next_note_num]
                location.end_page = next_location.start_page - 1
                
                # Asegurar que end_page no sea menor que start_page
                # (esto puede pasar si las notas están en la misma página)
                if location.end_page < location.start_page:
                    location.end_page = location.start_page
            else:
                # Para la última nota, el rango va hasta el final del documento
                location.end_page = total_pages

    return results

"""
Extractores de tablas usando diferentes motores (Camelot, Tabula, PDFPlumber)
Integrado con la lógica mejorada del playground
"""

import re
import logging
from pathlib import Path
from typing import List, Optional
from abc import ABC, abstractmethod

import pandas as pd
import pdfplumber

logger = logging.getLogger(__name__)


def try_import_camelot():
    """Intenta importar camelot de forma segura"""
    try:
        import camelot

        return camelot
    except ImportError:
        return None


def try_import_tabula():
    """Intenta importar tabula de forma segura"""
    try:
        import tabula

        return tabula
    except ImportError:
        return None


class TableExtractor(ABC):
    """Clase base abstracta para extractores de tablas"""

    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia y normaliza un DataFrame

        Args:
            df: DataFrame a limpiar

        Returns:
            DataFrame limpio y normalizado
        """
        if df.empty:
            return df

        # Eliminar filas y columnas completamente vacías
        df = df.dropna(how="all").dropna(axis=1, how="all")

        # Limpiar espacios en blanco excesivos
        df = df.map(
            lambda x: re.sub(r"\s+", " ", str(x)).strip()
            if pd.notna(x) and isinstance(x, str)
            else x
        )

        # Intentar convertir columnas numéricas
        for col in df.columns:
            try:
                # Remover caracteres no numéricos comunes en reportes financieros
                numeric_col = df[col].astype(str).str.replace("[,$%()]", "", regex=True)
                numeric_col = pd.to_numeric(numeric_col, errors="coerce")
                if numeric_col.notna().sum() > 0:
                    df[col] = numeric_col
            except:
                pass

        return df

    @staticmethod
    def is_valid_table(
        df: pd.DataFrame,
        min_cols: int = 2,
        min_rows: int = 4,
        max_empty_pct: float = 40.0,
        min_numeric_cols: int = 1,
    ) -> bool:
        """
        Valida si un DataFrame es realmente una tabla financiera estructurada

        FILTROS ESTRICTOS para evitar falsas detecciones en PDFs mal formateados

        Args:
            df: DataFrame a validar
            min_cols: Número mínimo de columnas
            min_rows: Número mínimo de filas
            max_empty_pct: Porcentaje máximo de celdas vacías permitido
            min_numeric_cols: Mínimo de columnas numéricas requeridas

        Returns:
            True si es una tabla financiera válida
        """
        if df.empty:
            return False

        # Filtro 1: Mínimo de columnas
        if df.shape[1] < min_cols:
            logger.debug(f"Tabla rechazada: solo {df.shape[1]} columna(s)")
            return False

        # Filtro 2: Mínimo de filas
        if df.shape[0] < min_rows:
            logger.debug(f"Tabla rechazada: solo {df.shape[0]} fila(s)")
            return False

        # Filtro 3: Porcentaje de celdas vacías
        total_cells = df.shape[0] * df.shape[1]
        empty_cells = df.isnull().sum().sum()
        empty_pct = (empty_cells / total_cells) * 100

        if empty_pct > max_empty_pct:
            logger.debug(f"Tabla rechazada: {empty_pct:.1f}% de celdas vacías")
            return False

        # Filtro 4: Detectar texto continuo mal formateado
        avg_length = df.astype(str).map(len).mean().mean()
        if avg_length > 100:
            logger.debug(f"Tabla rechazada: celdas muy largas ({avg_length:.0f} caracteres promedio)")
            return False

        # Filtro 5: CRÍTICO - Detectar texto pegado sin espacios
        def has_long_words(text):
            if pd.isna(text):
                return False
            words = str(text).split()
            return any(len(word) > 35 for word in words)

        text_cells = df.astype(str).map(has_long_words)
        long_word_pct = text_cells.sum().sum() / total_cells * 100

        if long_word_pct > 20:
            logger.debug(f"Tabla rechazada: {long_word_pct:.1f}% con texto pegado")
            return False

        # Filtro 6: OBLIGATORIO - Debe tener columnas numéricas
        # Las tablas financieras SIEMPRE tienen números
        numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
        if len(numeric_cols) < min_numeric_cols:
            logger.debug(f"Tabla rechazada: solo {len(numeric_cols)} columnas numéricas (mínimo {min_numeric_cols})")
            return False

        return True

    @abstractmethod
    def extract(self, pdf_path: Path, pages: str, **kwargs) -> List[pd.DataFrame]:
        """
        Extrae tablas del PDF

        Args:
            pdf_path: Ruta al archivo PDF
            pages: Páginas a procesar (formato: "1-5" o "1,3,5")
            **kwargs: Argumentos adicionales específicos del extractor

        Returns:
            Lista de DataFrames con las tablas extraídas
        """
        pass


class CamelotExtractor(TableExtractor):
    """Extractor de tablas usando la librería Camelot"""

    def __init__(self):
        self.camelot = try_import_camelot()
        if not self.camelot:
            raise RuntimeError(
                "Camelot no está disponible. Instala con: pip install camelot-py[cv]"
            )

    def extract(
        self,
        pdf_path: Path,
        pages: str,
        flavor_order: Optional[List[str]] = None,
        **kwargs,
    ) -> List[pd.DataFrame]:
        """
        Extrae tablas usando Camelot con diferentes estrategias

        Args:
            pdf_path: Ruta al archivo PDF
            pages: Páginas a procesar
            flavor_order: Lista de flavors a probar ['lattice', 'stream']
            **kwargs: Argumentos adicionales para Camelot

        Returns:
            Lista de DataFrames con las tablas extraídas
        """
        if flavor_order is None:
            flavor_order = ["lattice", "stream"]

        all_tables = []

        for flavor in flavor_order:
            try:
                logger.debug(
                    f"Intentando con Camelot flavor='{flavor}' en páginas {pages}"
                )

                tables = self.camelot.read_pdf(
                    str(pdf_path),
                    pages=pages,
                    flavor=flavor,
                    strip_text=" \n\t",
                    **kwargs,
                )

                if tables and tables.n > 0:
                    logger.info(
                        f"Encontradas {tables.n} tabla(s) con flavor='{flavor}'"
                    )

                    for table in tables:
                        # Verificar calidad de la tabla
                        if hasattr(table, "parsing_report"):
                            accuracy = table.parsing_report.get("accuracy", 0)
                            if accuracy < 50:
                                logger.warning(
                                    f"Tabla con baja precisión ({accuracy}%), "
                                    f"puede requerir revisión"
                                )

                        df = self.clean_dataframe(table.df)
                        if not df.empty and self.is_valid_table(df):
                            all_tables.append(df)
                        elif not df.empty:
                            logger.debug(f"Tabla descartada por filtros: {df.shape}")

                    if all_tables:
                        break  # Si encontramos tablas, no probar otros flavors

            except Exception as e:
                logger.debug(f"Error con flavor '{flavor}': {e}")
                continue

        return all_tables


class TabulaExtractor(TableExtractor):
    """Extractor de tablas usando la librería Tabula"""

    def __init__(self):
        self.tabula = try_import_tabula()
        if not self.tabula:
            raise RuntimeError(
                "Tabula no está disponible. Instala con: pip install tabula-py"
            )

    def extract(self, pdf_path: Path, pages: str, **kwargs) -> List[pd.DataFrame]:
        """
        Extrae tablas usando Tabula

        Args:
            pdf_path: Ruta al archivo PDF
            pages: Páginas a procesar
            **kwargs: Argumentos adicionales para Tabula

        Returns:
            Lista de DataFrames con las tablas extraídas
        """
        all_tables = []

        try:
            logger.debug(f"Extrayendo con Tabula en páginas {pages}")

            # Probar diferentes estrategias
            for strategy in ["lattice", "stream"]:
                try:
                    dfs = self.tabula.read_pdf(
                        str(pdf_path),
                        pages=pages,
                        lattice=(strategy == "lattice"),
                        multiple_tables=True,
                        pandas_options={"header": None},  # Sin asumir headers
                        **kwargs,
                    )

                    if dfs:
                        logger.info(
                            f"Encontradas {len(dfs)} tabla(s) con estrategia '{strategy}'"
                        )

                        for df in dfs:
                            cleaned = self.clean_dataframe(df)
                            if not cleaned.empty and self.is_valid_table(cleaned):
                                all_tables.append(cleaned)
                            elif not cleaned.empty:
                                logger.debug(f"Tabla descartada por filtros: {cleaned.shape}")

                        if all_tables:
                            break

                except Exception as e:
                    logger.debug(f"Error con estrategia '{strategy}': {e}")

        except Exception as e:
            logger.error(f"Error general con Tabula: {e}")

        return all_tables


class PDFPlumberExtractor(TableExtractor):
    """
    Extractor de tablas usando pdfplumber (más preciso y confiable).
    Basado en la lógica mejorada del playground.
    """

    def is_valid_table(
        self, 
        table_data: List[List], 
        min_rows: int = 2,
        min_cols: int = 2
    ) -> bool:
        """
        Valida si los datos extraídos son realmente una tabla.
        Implementa validaciones estrictas para evitar falsos positivos.
        
        Args:
            table_data: Los datos de la tabla extraída
            min_rows: Número mínimo de filas requeridas
            min_cols: Número mínimo de columnas requeridas
            
        Returns:
            True si es una tabla válida, False en caso contrario
        """
        if not table_data or len(table_data) < min_rows:
            return False
        
        # Verificar si tiene suficientes columnas
        if not table_data[0] or len(table_data[0]) < min_cols:
            return False
        
        # Verificar si las filas tienen un conteo de columnas consistente (con cierta tolerancia)
        col_counts = [len(row) for row in table_data]
        max_cols = max(col_counts)
        min_cols_in_data = min(col_counts)
        
        # Si el conteo de columnas varía demasiado, probablemente no es una tabla real
        if max_cols - min_cols_in_data > max_cols * 0.3:  # 30% de tolerancia
            return False
        
        # Verificar si la tabla tiene mayormente celdas vacías (probablemente no es una tabla real)
        total_cells = sum(col_counts)
        empty_cells = sum(
            1 for row in table_data 
            for cell in row 
            if cell is None or str(cell).strip() == ''
        )
        
        # Si más del 70% está vacío, probablemente no es una tabla real
        if total_cells > 0 and empty_cells / total_cells > 0.7:
            logger.debug(f"Tabla rechazada: {empty_cells/total_cells*100:.1f}% de celdas vacías")
            return False
        
        return True

    def extract(self, pdf_path: Path, pages: str, **kwargs) -> List[pd.DataFrame]:
        """
        Extrae tablas usando pdfplumber con validación robusta.
        
        Args:
            pdf_path: Ruta al archivo PDF
            pages: Páginas a procesar (formato: "1-5" o "1,3,5")
            **kwargs: Argumentos adicionales
            
        Returns:
            Lista de DataFrames con las tablas extraídas y validadas
        """
        all_tables = []
        
        # Parsear el rango de páginas
        page_numbers = self._parse_pages(pages)
        
        logger.debug(f"Extrayendo tablas de páginas {pages} usando pdfplumber...")
        
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                for page_num in page_numbers:
                    # Convertir a índice 0-based
                    page_idx = page_num - 1
                    
                    if page_idx >= len(pdf.pages):
                        break
                    
                    page = pdf.pages[page_idx]
                    
                    # Extraer tablas de esta página
                    page_tables = page.extract_tables()
                    
                    if page_tables:
                        for i, table_data in enumerate(page_tables):
                            # Validar si es una tabla real
                            if self.is_valid_table(table_data):
                                try:
                                    # Convertir a DataFrame
                                    # La primera fila se usa como encabezado
                                    df = pd.DataFrame(table_data[1:], columns=table_data[0])
                                    
                                    # Limpiar el DataFrame
                                    df = self.clean_dataframe(df)
                                    
                                    if not df.empty:
                                        all_tables.append(df)
                                        logger.debug(f"✓ Tabla válida encontrada en página {page_num}")
                                except Exception as e:
                                    logger.debug(f"Error convirtiendo tabla en página {page_num}: {e}")
                            else:
                                logger.debug(f"✗ Tabla inválida omitida en página {page_num}")
            
            logger.info(f"Total de tablas válidas encontradas: {len(all_tables)}")
        
        except Exception as e:
            logger.error(f"Error extrayendo tablas con pdfplumber: {e}")
        
        return all_tables
    
    def _parse_pages(self, pages: str) -> List[int]:
        """
        Parsea una cadena de páginas a una lista de números de página.
        
        Args:
            pages: Cadena de páginas (ej: "1-5", "1,3,5", "1-3,5-7")
            
        Returns:
            Lista de números de página
        """
        page_numbers = []
        
        # Dividir por comas
        parts = pages.split(',')
        
        for part in parts:
            part = part.strip()
            
            if '-' in part:
                # Es un rango
                start, end = map(int, part.split('-'))
                page_numbers.extend(range(start, end + 1))
            else:
                # Es un número individual
                page_numbers.append(int(part))
        
        return sorted(set(page_numbers))

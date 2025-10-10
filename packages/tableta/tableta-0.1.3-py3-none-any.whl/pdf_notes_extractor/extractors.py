"""
Extractores de tablas usando diferentes motores (Camelot, Tabula)
"""

import re
import logging
from pathlib import Path
from typing import List, Optional
from abc import ABC, abstractmethod

import pandas as pd

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
        df = df.applymap(
            lambda x: re.sub(r"\s+", " ", str(x)).strip()
            if pd.notna(x) and isinstance(x, str)
            else x
        )

        # Intentar convertir columnas numéricas
        for col in df.columns:
            try:
                # Remover caracteres no numéricos comunes en reportes financieros
                numeric_col = df[col].astype(str).str.replace("[,$%()]", "", regex=True)
                numeric_col = pd.to_numeric(numeric_col, errors="ignore")
                if numeric_col.dtype in ["float64", "int64"]:
                    df[col] = numeric_col
            except:
                pass

        return df

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
                        if not df.empty:
                            all_tables.append(df)

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
                            if not cleaned.empty:
                                all_tables.append(cleaned)

                        if all_tables:
                            break

                except Exception as e:
                    logger.debug(f"Error con estrategia '{strategy}': {e}")

        except Exception as e:
            logger.error(f"Error general con Tabula: {e}")

        return all_tables

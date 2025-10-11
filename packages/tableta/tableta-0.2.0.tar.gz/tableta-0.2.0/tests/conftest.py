"""
Configuración de pytest y fixtures compartidos
"""

import pytest
import pandas as pd
from pathlib import Path


@pytest.fixture
def sample_dataframe():
    """Fixture con un DataFrame de ejemplo"""
    return pd.DataFrame(
        {
            "Concepto": ["Activos", "Pasivos", "Patrimonio"],
            "2024": [1000, 600, 400],
            "2023": [900, 500, 400],
        }
    )


@pytest.fixture
def sample_dataframe_with_nulls():
    """Fixture con un DataFrame que tiene valores nulos"""
    return pd.DataFrame(
        {"A": [1, None, 3, None], "B": [None, 2, 3, None], "C": [1, 2, None, None]}
    )


@pytest.fixture
def temp_output_dir(tmp_path):
    """Fixture con un directorio temporal para outputs"""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir

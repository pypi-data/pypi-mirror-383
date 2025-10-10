"""
Tests para los modelos de datos
"""

import pytest
import pandas as pd
from pdf_notes_extractor.models import NoteLocation, ExtractionResult


class TestNoteLocation:
    """Tests para NoteLocation"""

    def test_pages_range_single_page(self):
        """Test cuando la nota está en una sola página"""
        location = NoteLocation(number=1, start_page=5, end_page=5)
        assert location.pages_range() == "5"

    def test_pages_range_multiple_pages(self):
        """Test cuando la nota abarca múltiples páginas"""
        location = NoteLocation(number=1, start_page=5, end_page=8)
        assert location.pages_range() == "5-8"

    def test_note_location_creation(self):
        """Test creación básica de NoteLocation"""
        location = NoteLocation(number=3, start_page=10, end_page=15, char_position=100)
        assert location.number == 3
        assert location.start_page == 10
        assert location.end_page == 15
        assert location.char_position == 100


class TestExtractionResult:
    """Tests para ExtractionResult"""

    def test_has_tables_true(self):
        """Test has_tables cuando hay tablas"""
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        result = ExtractionResult(
            note_number=1, tables=[df], pages_processed="5-8", extraction_time=1.5
        )
        assert result.has_tables is True
        assert result.table_count == 1

    def test_has_tables_false(self):
        """Test has_tables cuando no hay tablas"""
        result = ExtractionResult(
            note_number=1, tables=[], pages_processed="5-8", extraction_time=1.5
        )
        assert result.has_tables is False
        assert result.table_count == 0

    def test_warnings_default(self):
        """Test que warnings tiene valor por defecto"""
        result = ExtractionResult(
            note_number=1, tables=[], pages_processed="5", extraction_time=0.5
        )
        assert result.warnings == []

    def test_warnings_with_messages(self):
        """Test con mensajes de advertencia"""
        result = ExtractionResult(
            note_number=1,
            tables=[],
            pages_processed="5",
            extraction_time=0.5,
            warnings=["Warning 1", "Warning 2"],
        )
        assert len(result.warnings) == 2
        assert "Warning 1" in result.warnings

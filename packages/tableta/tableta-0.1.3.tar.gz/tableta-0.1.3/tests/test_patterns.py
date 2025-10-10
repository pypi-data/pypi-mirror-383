"""
Tests para los patrones de detección de notas
"""

import pytest
from pdf_notes_extractor.patterns import NotePatterns


class TestNotePatterns:
    """Tests para NotePatterns"""

    def test_main_pattern_basic(self):
        """Test detección básica de nota"""
        text = "Nota 1\nAlgún contenido"
        matches = NotePatterns.find_all(text)
        assert len(matches) == 1
        assert matches[0][1] == 1

    def test_main_pattern_with_number_sign(self):
        """Test con Nº"""
        text = "Nota Nº 5\nContenido"
        matches = NotePatterns.find_all(text)
        assert len(matches) == 1
        assert matches[0][1] == 5

    def test_main_pattern_with_dot(self):
        """Test con N."""
        text = "Nota N. 10\nContenido"
        matches = NotePatterns.find_all(text)
        assert len(matches) == 1
        assert matches[0][1] == 10

    def test_multiple_notes(self):
        """Test con múltiples notas"""
        text = """
        Nota 1
        Contenido de nota 1
        
        Nota 2
        Contenido de nota 2
        
        Nota 3
        Contenido de nota 3
        """
        matches = NotePatterns.find_all(text)
        assert len(matches) == 3
        note_numbers = [m[1] for m in matches]
        assert note_numbers == [1, 2, 3]

    def test_english_pattern(self):
        """Test patrón en inglés"""
        text = "Note 5\nContent"
        matches = NotePatterns.find_all(text)
        assert len(matches) == 1
        assert matches[0][1] == 5

    def test_anexo_pattern(self):
        """Test patrón de anexo"""
        text = "Anexo 7\nContenido"
        matches = NotePatterns.find_all(text)
        assert len(matches) == 1
        assert matches[0][1] == 7

    def test_no_matches(self):
        """Test cuando no hay coincidencias"""
        text = "Contenido sin notas"
        matches = NotePatterns.find_all(text)
        assert len(matches) == 0

    def test_case_insensitive(self):
        """Test que el patrón es case-insensitive"""
        text = "NOTA 1\nnota 2\nNoTa 3"
        matches = NotePatterns.find_all(text)
        assert len(matches) == 3

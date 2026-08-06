import pytest
from utils.number_to_words import number_to_words_es


class TestNumberToWords:
    """Tests for number_to_words utility function"""

    def test_basic_amount(self):
        """Test basic amount conversion"""
        result = number_to_words_es(100.00)
        assert "Cien" in result
        assert "00/100 Bolivianos" in result

    def test_decimal_amount(self):
        """Test amount with decimals"""
        result = number_to_words_es(1523.50)
        assert "Mil" in result
        assert "Veintitrés" in result or "veintitres" in result
        assert "50/100 Bolivianos" in result

    def test_zero(self):
        """Test zero amount"""
        result = number_to_words_es(0)
        assert "Cero" in result

    def test_small_amount(self):
        """Test small amount"""
        result = number_to_words_es(1.00)
        assert "Uno" in result

    def test_thousands(self):
        """Test thousands"""
        result = number_to_words_es(2000.00)
        assert "Dos mil" in result

    def test_millions(self):
        """Test millions"""
        result = number_to_words_es(1000000.00)
        assert "Un millón" in result
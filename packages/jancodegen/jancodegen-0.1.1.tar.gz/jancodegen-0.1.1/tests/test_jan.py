import pytest
from jancodegen import jan


class TestJANCodeGenerator:
    """Test suite for JAN code generation functions."""

    def test_get_last_jan_digit(self):
        """Test the check digit calculation function."""
        # Test cases with known valid codes
        test_cases = [
            ("12345678901", 2),  # GTIN-12 example
            ("01234567890", 5),  # Another example
            ("99999999999", 3),  # Edge case with 9s
            ("00000000000", 0),  # Edge case with 0s
        ]

        for code, expected_check in test_cases:
            assert jan._get_last_jan_digit(code) == expected_check

    def test_random_gtin_13(self):
        """Test GTIN-13 code generation."""
        code = jan.random_gtin_13()

        # Check length
        assert len(code) == 13

        # Check all characters are digits
        assert code.isdigit()

        # Check check digit is valid
        base_code = code[:-1]
        expected_check = jan._get_last_jan_digit(base_code)
        assert int(code[-1]) == expected_check

        # Check randomness (generate multiple and ensure they're different)
        codes = [jan.random_gtin_13() for _ in range(10)]
        assert len(set(codes)) > 1  # At least some should be different

    def test_random_gtin_8(self):
        """Test GTIN-8 code generation."""
        code = jan.random_gtin_8()

        # Check length
        assert len(code) == 8

        # Check all characters are digits
        assert code.isdigit()

        # Check check digit is valid
        base_code = code[:-1]
        expected_check = jan._get_last_jan_digit(base_code)
        assert int(code[-1]) == expected_check

    def test_random_gtin_14(self):
        """Test GTIN-14 code generation."""
        code = jan.random_gtin_14()

        # Check length
        assert len(code) == 14

        # Check all characters are digits
        assert code.isdigit()

        # Check starts with '1'
        assert code.startswith('1')

        # Check check digit is valid
        base_code = code[:-1]
        expected_check = jan._get_last_jan_digit(base_code)
        assert int(code[-1]) == expected_check

    def test_random_upc_12(self):
        """Test UPC-12 code generation."""
        code = jan.random_upc_12()

        # Check length
        assert len(code) == 12

        # Check all characters are digits
        assert code.isdigit()

        # Check check digit is valid
        base_code = code[:-1]
        expected_check = jan._get_last_jan_digit(base_code)
        assert int(code[-1]) == expected_check

    def test_random_sscc_18(self):
        """Test SSCC-18 code generation."""
        code = jan.random_sscc_18()

        # Check length
        assert len(code) == 18

        # Check all characters are digits
        assert code.isdigit()

        # Check starts with '0'
        assert code.startswith('0')

        # Check check digit is valid
        base_code = code[:-1]
        expected_check = jan._get_last_jan_digit(base_code)
        assert int(code[-1]) == expected_check

    def test_random_grai_14(self):
        """Test GRAI-14 code generation."""
        code = jan.random_grai_14()

        # Check length
        assert len(code) == 14

        # Check all characters are digits
        assert code.isdigit()

        # Check starts with '0'
        assert code.startswith('0')

        # Check check digit is valid
        base_code = code[:-1]
        expected_check = jan._get_last_jan_digit(base_code)
        assert int(code[-1]) == expected_check

    @pytest.mark.parametrize("func,expected_length,prefix", [
        (jan.random_gtin_13, 13, None),
        (jan.random_gtin_8, 8, None),
        (jan.random_gtin_14, 14, '1'),
        (jan.random_upc_12, 12, None),
        (jan.random_sscc_18, 18, '0'),
        (jan.random_grai_14, 14, '0'),
    ])
    def test_all_functions_return_valid_codes(self, func, expected_length, prefix):
        """Parameterized test for all generation functions."""
        code = func()

        # Check length
        assert len(code) == expected_length

        # Check all characters are digits
        assert code.isdigit()

        # Check prefix if specified
        if prefix:
            assert code.startswith(prefix)

        # Check check digit is valid
        base_code = code[:-1]
        expected_check = jan._get_last_jan_digit(base_code)
        assert int(code[-1]) == expected_check

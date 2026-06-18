from src.utils import clean_address, is_valid_tc


class TestIsValidTc:
    def test_valid_tc(self):
        assert is_valid_tc("12345678901") is True

    def test_invalid_length_short(self):
        assert is_valid_tc("12345") is False

    def test_invalid_length_long(self):
        assert is_valid_tc("123456789012") is False

    def test_invalid_all_zeros(self):
        assert is_valid_tc("00000000000") is False

    def test_invalid_non_digits(self):
        assert is_valid_tc("12345abcde") is False

    def test_empty_string(self):
        assert is_valid_tc("") is False

    def test_none_value(self):
        assert is_valid_tc(None) is False

    def test_valid_tc_all_digits(self):
        assert is_valid_tc("00000000001") is True


class TestCleanAddress:
    def test_empty_string(self):
        assert clean_address("") == ""

    def test_none_value(self):
        assert clean_address(None) == ""

    def test_normal_address(self):
        result = clean_address("İstanbul Kadıköy")
        assert result == "İstanbul Kadıköy"

    def test_address_with_trailing_pattern(self):
        result = clean_address("Atatürk Mahallesi Cadde Sokak No:5")
        assert result == "Atatürk Mahallesi"

    def test_address_single_word(self):
        result = clean_address("İstanbul")
        assert result == "İstanbul"

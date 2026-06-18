import re

_ADDRESS_PATTERN = re.compile(r"\s+(\S+\s+){2}\S+$")


def is_valid_tc(tc: str | None) -> bool:
    """TC numarasının geçerli bir formatta olup olmadığını kontrol eder."""
    return bool(tc and tc.isdigit() and len(tc) == 11 and tc != "00000000000")


def clean_address(address: str | None) -> str:
    """Adres bilgisindeki gereksiz desenleri temizler."""
    if not address:
        return ""
    return _ADDRESS_PATTERN.sub("", address).strip()


def clean_value(val: object) -> str:
    """Değer temizliği: boş, 'None' veya sadece 'YOK' kelimelerinden oluşan değerleri boş string'e çevirir."""
    s_val = str(val).strip()
    if not s_val or s_val == "None" or all(word == "YOK" for word in s_val.split()):
        return ""
    return s_val

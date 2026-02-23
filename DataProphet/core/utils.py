import re

def is_valid_tc(tc: str) -> bool:
    """TC numarasının geçerli bir formatta olup olmadığını kontrol eder."""
    return bool(tc and tc.isdigit() and len(tc) == 11 and tc != "00000000000")

def clean_address(address: str) -> str:
    """Adres bilgisindeki gereksiz desenleri temizler."""
    if not address:
        return ""
    # Adresin sonundaki belirli desenleri temizle
    return re.sub(r'\s+(\S+\s+){2}\S+$', '', address).strip()

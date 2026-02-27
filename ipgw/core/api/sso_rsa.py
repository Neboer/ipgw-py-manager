import re
from base64 import b64decode
from base64 import b64encode
from secrets import token_bytes
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from requests import Session

from .SSO_error import BackendError

RSA_PADDING_OVERHEAD = 11


def extract_login_page_rsa_public_key(session: Session, page_soup: BeautifulSoup) -> str:
    login_js_src = None
    for script_tag in page_soup.find_all("script", src=True):
        script_src = script_tag.attrs.get("src", "")
        if "login_neu.js" in script_src:
            login_js_src = script_src
            break
    if not login_js_src:
        raise BackendError("cannot find login_neu.js from SSO login page")

    login_js_url = urljoin("https://pass.neu.edu.cn", login_js_src)
    login_js_text = session.get(login_js_url).text
    public_key_match = re.search(r'publicKeyStr\s*=\s*"([^"]+)"', login_js_text)
    if not public_key_match:
        raise BackendError("cannot extract publicKeyStr from login_neu.js")
    return public_key_match.group(1)


def _read_der_tlv(der_bytes: bytes, offset: int):
    if offset >= len(der_bytes):
        raise ValueError("invalid DER: unexpected end of data")
    tag = der_bytes[offset]
    offset += 1
    if offset >= len(der_bytes):
        raise ValueError("invalid DER: missing length")
    first_length = der_bytes[offset]
    offset += 1
    if first_length & 0x80:
        length_bytes_count = first_length & 0x7F
        if length_bytes_count == 0 or offset + length_bytes_count > len(der_bytes):
            raise ValueError("invalid DER: bad long-form length")
        length = int.from_bytes(der_bytes[offset:offset + length_bytes_count], "big")
        offset += length_bytes_count
    else:
        length = first_length
    if offset + length > len(der_bytes):
        raise ValueError("invalid DER: value out of bounds")
    value = der_bytes[offset:offset + length]
    return tag, value, offset + length


def _decode_rsa_public_key(public_key_b64: str):
    spki_der = b64decode(public_key_b64)
    seq_tag, spki_seq, seq_end = _read_der_tlv(spki_der, 0)
    if seq_tag != 0x30 or seq_end != len(spki_der):
        raise ValueError("invalid SubjectPublicKeyInfo structure")

    _, _, cursor = _read_der_tlv(spki_seq, 0)
    bit_string_tag, bit_string_value, cursor = _read_der_tlv(spki_seq, cursor)
    if bit_string_tag != 0x03 or not bit_string_value or bit_string_value[0] != 0:
        raise ValueError("invalid SubjectPublicKeyInfo BIT STRING")
    if cursor != len(spki_seq):
        raise ValueError("invalid SubjectPublicKeyInfo trailing bytes")

    rsa_der = bit_string_value[1:]
    rsa_seq_tag, rsa_seq, rsa_end = _read_der_tlv(rsa_der, 0)
    if rsa_seq_tag != 0x30 or rsa_end != len(rsa_der):
        raise ValueError("invalid RSAPublicKey structure")
    modulus_tag, modulus_bytes, cursor = _read_der_tlv(rsa_seq, 0)
    exponent_tag, exponent_bytes, cursor = _read_der_tlv(rsa_seq, cursor)
    if modulus_tag != 0x02 or exponent_tag != 0x02 or cursor != len(rsa_seq):
        raise ValueError("invalid RSAPublicKey fields")

    modulus = int.from_bytes(modulus_bytes, "big")
    exponent = int.from_bytes(exponent_bytes, "big")
    key_bytes = len(modulus_bytes) - 1 if modulus_bytes.startswith(b"\x00") else len(modulus_bytes)
    return modulus, exponent, key_bytes


def rsa_encrypt_username_password(username: str, password: str, public_key_b64: str) -> str:
    modulus, exponent, key_bytes = _decode_rsa_public_key(public_key_b64)
    plaintext = (username + password).encode("utf-8")
    max_plaintext_len = key_bytes - RSA_PADDING_OVERHEAD
    if len(plaintext) > max_plaintext_len:
        raise ValueError("username+password is too long for RSA key size")

    padding_len = key_bytes - len(plaintext) - 3
    padding = b""
    while len(padding) < padding_len:
        block = token_bytes(padding_len - len(padding))
        padding += block.replace(b"\x00", b"")
    encoded_message = b"\x00\x02" + padding[:padding_len] + b"\x00" + plaintext
    cipher_int = pow(int.from_bytes(encoded_message, "big"), exponent, modulus)
    return b64encode(cipher_int.to_bytes(key_bytes, "big")).decode("ascii")

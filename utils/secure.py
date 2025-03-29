"""функции хэширования"""
import base64
import hashlib


def base64_hasher(hash_str: str) -> str:
    """функция хэширования строка в base64"""
    _hash = hashlib.md5(hash_str.encode('utf-8')).digest()
    encoded_hash = base64.urlsafe_b64encode(_hash).decode('utf-8').rstrip('=')
    return encoded_hash

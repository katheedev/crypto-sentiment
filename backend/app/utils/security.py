from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet


def build_fernet(master_key: str) -> Fernet:
    digest = hashlib.sha256(master_key.encode("utf-8")).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def encrypt_text(master_key: str, raw: str) -> str:
    return build_fernet(master_key).encrypt(raw.encode("utf-8")).decode("utf-8")


def decrypt_text(master_key: str, encrypted: str) -> str:
    return build_fernet(master_key).decrypt(encrypted.encode("utf-8")).decode("utf-8")

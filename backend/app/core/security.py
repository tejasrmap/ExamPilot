import os
import re
import base64
import hashlib
import secrets
from typing import Optional, Tuple, List
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from jose import jwt, JWTError
from passlib.context import CryptContext
from backend.app.core.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def _derive_key(secret_str: str) -> bytes:
    """Derives a deterministic 32-byte (256-bit) AES key from a secret string."""
    return hashlib.sha256(secret_str.strip().encode("utf-8")).digest()

def _get_encryption_keys() -> List[bytes]:
    """
    Returns list of encryption keys for zero-downtime key rotation.
    Primary key is always at index 0, followed by any configured rotation keys.
    """
    keys = [_derive_key(settings.API_KEY_ENCRYPTION_SECRET)]
    for rot in getattr(settings, "API_KEY_ENCRYPTION_ROTATION_SECRETS", []):
        if rot.strip():
            k = _derive_key(rot)
            if k not in keys:
                keys.append(k)
    return keys

def encrypt_api_key(plain_key: str) -> str:
    """
    Encrypts a user API key using AES-256-GCM with a fresh random 96-bit nonce.
    Always uses the active primary encryption key.
    Returns URL-safe base64 string: nonce (12 bytes) + ciphertext + auth tag (16 bytes).
    """
    if not plain_key:
        raise ValueError("Cannot encrypt an empty key")
    
    primary_key = _get_encryption_keys()[0]
    aesgcm = AESGCM(primary_key)
    nonce = os.urandom(12)  # 96-bit nonce
    data = plain_key.strip().encode("utf-8")
    ciphertext = aesgcm.encrypt(nonce, data, None)
    
    payload = nonce + ciphertext
    return base64.urlsafe_b64encode(payload).decode("utf-8")

def decrypt_api_key(encrypted_blob: str) -> str:
    """
    Decrypts an AES-256-GCM encrypted API key.
    Attempts decryption with the primary key first, and falls back to
    configured rotation secrets to enable seamless key rotation without data loss.
    """
    if not encrypted_blob:
        raise ValueError("Cannot decrypt empty payload")
    
    try:
        payload = base64.urlsafe_b64decode(encrypted_blob.encode("utf-8"))
        if len(payload) < 28: # 12 bytes nonce + 16 bytes tag minimum
            raise ValueError("Invalid encrypted payload length")
        
        nonce = payload[:12]
        ciphertext = payload[12:]
        
        # Try primary key, then rotation keys
        last_err = None
        for key in _get_encryption_keys():
            try:
                aesgcm = AESGCM(key)
                decrypted = aesgcm.decrypt(nonce, ciphertext, None)
                return decrypted.decode("utf-8")
            except Exception as e:
                last_err = e
                continue
                
        raise ValueError(f"Decryption failed across all active keys: {str(last_err)}")
    except Exception as e:
        raise ValueError(f"Failed to decrypt API key: {str(e)}")

def mask_api_key(plain_key: str) -> str:
    """
    Masks sensitive API key according to SaaS requirements:
    e.g. sk-proj-••••••••••••1234 or AIzaSy••••••••••••9876
    """
    clean = plain_key.strip()
    if len(clean) <= 8:
        return "••••••••"
    
    prefix_len = min(6, len(clean) // 4)
    suffix_len = min(4, len(clean) // 4)
    
    prefix = clean[:prefix_len]
    suffix = clean[-suffix_len:]
    dots = "•" * 12
    return f"{prefix}{dots}{suffix}"

def validate_password_strength(password: str) -> None:
    """
    Validates password strength according to production security policy:
    - Minimum 8 characters
    - Contains at least one letter (a-z, A-Z)
    - Contains at least one number or special character
    """
    if not password or len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if not re.search(r"[a-zA-Z]", password):
        raise ValueError("Password must contain at least one letter.")
    if not re.search(r"[0-9!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Password must contain at least one number or special character.")

def generate_secure_reset_token() -> Tuple[str, str]:
    """
    Generates a cryptographically secure, high-entropy single-use password reset token.
    Returns:
        (raw_token, token_hash)
        raw_token: 43-character URL-safe string delivered only via email.
        token_hash: SHA-256 hex digest stored in the database.
    """
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    return raw_token, token_hash

def hash_token(raw_token: str) -> str:
    """Computes SHA-256 hash of a plain token string."""
    return hashlib.sha256(raw_token.strip().encode("utf-8")).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

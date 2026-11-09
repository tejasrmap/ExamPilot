import os
import base64
import hashlib
from typing import Optional, Tuple
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from jose import jwt, JWTError
from passlib.context import CryptContext
from backend.app.core.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def _get_encryption_key() -> bytes:
    """
    Derive a deterministic 32-byte (256-bit) key from settings.API_KEY_ENCRYPTION_SECRET
    using SHA-256.
    """
    secret = settings.API_KEY_ENCRYPTION_SECRET.encode("utf-8")
    return hashlib.sha256(secret).digest()

def encrypt_api_key(plain_key: str) -> str:
    """
    Encrypts a user API key using AES-256-GCM.
    Returns URL-safe base64 string combining 12-byte nonce + ciphertext + 16-byte auth tag.
    """
    if not plain_key:
        raise ValueError("Cannot encrypt an empty key")
    
    key = _get_encryption_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # Standard 96-bit nonce for AES-GCM
    data = plain_key.strip().encode("utf-8")
    ciphertext = aesgcm.encrypt(nonce, data, None)
    
    # Combined payload: nonce + ciphertext
    payload = nonce + ciphertext
    return base64.urlsafe_b64encode(payload).decode("utf-8")

def decrypt_api_key(encrypted_blob: str) -> str:
    """
    Decrypts an AES-256-GCM encrypted API key.
    Raises ValueError on tampering or invalid key.
    """
    if not encrypted_blob:
        raise ValueError("Cannot decrypt empty payload")
    
    try:
        payload = base64.urlsafe_b64decode(encrypted_blob.encode("utf-8"))
        if len(payload) < 28: # 12 bytes nonce + 16 bytes tag minimum
            raise ValueError("Invalid encrypted payload length")
        
        nonce = payload[:12]
        ciphertext = payload[12:]
        key = _get_encryption_key()
        aesgcm = AESGCM(key)
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted.decode("utf-8")
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

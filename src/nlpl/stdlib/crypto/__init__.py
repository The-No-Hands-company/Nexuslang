"""
Cryptography and Hashing for NLPL.
"""

import hashlib
import hmac
import base64
import secrets
from typing import Optional
from ...runtime.runtime import Runtime


def hash_md5(data: str, encoding: str = 'utf-8') -> str:
    """Compute MD5 hash."""
    return hashlib.md5(data.encode(encoding)).hexdigest()


def hash_sha1(data: str, encoding: str = 'utf-8') -> str:
    """Compute SHA-1 hash."""
    return hashlib.sha1(data.encode(encoding)).hexdigest()


def hash_sha256(data: str, encoding: str = 'utf-8') -> str:
    """Compute SHA-256 hash."""
    return hashlib.sha256(data.encode(encoding)).hexdigest()


def hash_sha512(data: str, encoding: str = 'utf-8') -> str:
    """Compute SHA-512 hash."""
    return hashlib.sha512(data.encode(encoding)).hexdigest()


def hash_sha3_256(data: str, encoding: str = 'utf-8') -> str:
    """Compute SHA3-256 hash."""
    return hashlib.sha3_256(data.encode(encoding)).hexdigest()


def hash_sha3_512(data: str, encoding: str = 'utf-8') -> str:
    """Compute SHA3-512 hash."""
    return hashlib.sha3_512(data.encode(encoding)).hexdigest()


def hash_blake2b(data: str, encoding: str = 'utf-8') -> str:
    """Compute BLAKE2b hash."""
    return hashlib.blake2b(data.encode(encoding)).hexdigest()


def hash_blake2s(data: str, encoding: str = 'utf-8') -> str:
    """Compute BLAKE2s hash."""
    return hashlib.blake2s(data.encode(encoding)).hexdigest()


def hmac_sha256(data: str, key: str, encoding: str = 'utf-8') -> str:
    """Compute HMAC-SHA256."""
    return hmac.new(key.encode(encoding), data.encode(encoding), hashlib.sha256).hexdigest()


def hmac_sha512(data: str, key: str, encoding: str = 'utf-8') -> str:
    """Compute HMAC-SHA512."""
    return hmac.new(key.encode(encoding), data.encode(encoding), hashlib.sha512).hexdigest()


def base64_encode(data: str, encoding: str = 'utf-8') -> str:
    """Encode string to base64."""
    return base64.b64encode(data.encode(encoding)).decode('ascii')


def base64_decode(data: str, encoding: str = 'utf-8') -> str:
    """Decode base64 to string."""
    return base64.b64decode(data).decode(encoding)


def base64_url_encode(data: str, encoding: str = 'utf-8') -> str:
    """Encode string to URL-safe base64."""
    return base64.urlsafe_b64encode(data.encode(encoding)).decode('ascii')


def base64_url_decode(data: str, encoding: str = 'utf-8') -> str:
    """Decode URL-safe base64 to string."""
    return base64.urlsafe_b64decode(data).decode(encoding)


def random_bytes(n: int) -> bytes:
    """Generate n random bytes (cryptographically secure)."""
    return secrets.token_bytes(n)


def random_hex(n: int) -> str:
    """Generate random hex string of n bytes."""
    return secrets.token_hex(n)


def random_token(n: int = 32) -> str:
    """Generate random URL-safe token."""
    return secrets.token_urlsafe(n)


def compare_digest(a: str, b: str) -> bool:
    """Constant-time string comparison (prevents timing attacks)."""
    return hmac.compare_digest(a, b)


def hash_password(password: str, salt: Optional[str] = None) -> dict:
    """
    Hash password with salt (basic implementation).
    Returns dict with 'hash' and 'salt'.
    Note: For production, use proper password hashing like bcrypt or argon2.
    """
    if salt is None:
        salt = random_hex(16)
    
    # Simple PBKDF2 with SHA-256
    import hashlib
    hash_value = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), 
                                      salt.encode('utf-8'), 100000)
    
    return {
        'hash': hash_value.hex(),
        'salt': salt,
        'algorithm': 'pbkdf2_sha256',
        'iterations': 100000
    }


def verify_password(password: str, hash_info: dict) -> bool:
    """Verify password against hash."""
    salt = hash_info.get('salt')
    expected_hash = hash_info.get('hash')
    
    if not salt or not expected_hash:
        return False
    
    # Recompute hash
    hash_value = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'),
                                      salt.encode('utf-8'), 100000)
    
    return compare_digest(hash_value.hex(), expected_hash)


def register_crypto_functions(runtime: Runtime) -> None:
    """Register cryptography functions with the runtime."""
    
    # Hashing
    runtime.register_function("hash_md5", hash_md5)
    runtime.register_function("hash_sha1", hash_sha1)
    runtime.register_function("hash_sha256", hash_sha256)
    runtime.register_function("hash_sha512", hash_sha512)
    runtime.register_function("hash_sha3_256", hash_sha3_256)
    runtime.register_function("hash_sha3_512", hash_sha3_512)
    runtime.register_function("hash_blake2b", hash_blake2b)
    runtime.register_function("hash_blake2s", hash_blake2s)
    
    # HMAC
    runtime.register_function("hmac_sha256", hmac_sha256)
    runtime.register_function("hmac_sha512", hmac_sha512)
    
    # Base64
    runtime.register_function("base64_encode", base64_encode)
    runtime.register_function("base64_decode", base64_decode)
    runtime.register_function("base64_url_encode", base64_url_encode)
    runtime.register_function("base64_url_decode", base64_url_decode)
    
    # Random
    runtime.register_function("random_bytes", random_bytes)
    runtime.register_function("random_hex", random_hex)
    runtime.register_function("random_token", random_token)
    
    # Security
    runtime.register_function("compare_digest", compare_digest)
    runtime.register_function("hash_password", hash_password)
    runtime.register_function("verify_password", verify_password)
    
    # Aliases
    runtime.register_function("md5", hash_md5)
    runtime.register_function("sha256", hash_sha256)
    runtime.register_function("sha512", hash_sha512)

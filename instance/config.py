from pathlib import Path

OP_EC_PUBLIC_KEY = b"""
-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEcducjB1i+21VSynA6E9VXXjGCc4HgCUs7dHTdgcQIs+T0BRqzgdOlrG4ITiGk+s8Rcc5cH0GYP3UV/QZ2ocl0w==
-----END PUBLIC KEY-----"""

# NOTE secret to be used for a single salt-deriving party
HASH_SALT_SECRET = bytes.fromhex(
    "8952d7b37e1c860c88b8a5dc196219d507dcd6b6e259db03b9e91a4a24fce9b4"
)


def load_private_key():
    with open(Path(__file__).parent / "salt-X25519key.pem", "rb") as handle:
        return handle.read()


def load_public_key():
    with open(Path(__file__).parent / "salt-X25519key.pem.pub", "r") as handle:
        return handle.read()


X25519_PRIVATE_KEY = load_private_key()
X25519_PUBLIC_KEY = load_public_key()

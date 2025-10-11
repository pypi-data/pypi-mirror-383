"""This script contains MultiCrypt's user API.
It is the single interface to the multitude of cryptographic algorithms living
in ./algorithms.
"""

from pkgutil import walk_packages
from importlib import import_module
from . import algorithms
from .algorithms import rsa, ec_secp256k1


crypto_modules = {"EC-secp256k1": ec_secp256k1, "RSA": rsa}

# A SHAME TO DISABLE THE FOLLOWING,
# 'twas such a neat pythonic zero-boilerplate solution!
# # load all cryptographic family modules from the algorithms folder
# for loader, module_name, is_pkg in walk_packages(path=algorithms.__path__):
#     module = import_module(f"{algorithms.__name__}.{module_name}")
#     if module.FAMILY_NAME in crypto_modules:
#         continue
#     crypto_modules.update({module.FAMILY_NAME: module})
#     print(module.FAMILY_NAME)


def generate_keys(family: str, **kwargs):
    """Generate a pair of public and private keys to be used with the specified
    family.
    Args:
        family (str): the cryptographic family of the keys
        keylength (int): the number of bits the key is composed of
    Returns:
        tuple: tuple of bytess, a public key and a private key
    """
    return crypto_modules[family].generate_keys(**kwargs)


def derive_public_key(family: str, private_key: bytes) -> bytes:
    """Given a private key, generate the corresponding public key.
    Args:
        family (str): the cryptographic family of the keys
        private_key (bytes): the private key
    Returns:
        bytes: the public key
    """
    return crypto_modules[family].derive_public_key(private_key)


def encrypt(
    family: str,
    data_to_encrypt: bytes,
    public_key: bytes,
    encryption_options: str | None = None,
):
    """Encrypt the provided data using the specified public key and encryption
    family.
    Args:
        family (str): the cryptographic family to be used for the encryption
        data_to_encrypt (bytes): the data to encrypt
        public_key (bytes): the public key to be used for the encryption
        encryption_options (str): specification code for which
                                encryption/decryption protocol should be used
    Returns:
        bytes: the encrypted data
    """
    return crypto_modules[family].encrypt(
        data_to_encrypt, public_key, encryption_options
    )


def decrypt(
    family: str,
    data_to_decrypt: bytes,
    private_key: bytes,
    encryption_options: str | None = None,
):
    """Decrypt the provided data using the specified private key and encryption
    family.
    Args:
        family (str): the cryptographic family to be used for the decryption
        data_to_decrypt (bytes): the data to decrypt
        private_key (bytes): the private key to be used for the decryption
        encryption_options (str): specification code for which
                                encryption/decryption protocol should be used
    Returns:
        bytes: the decrypted data
    """
    return crypto_modules[family].decrypt(
        data_to_decrypt, private_key, encryption_options
    )


def sign(
    family: str,
    data: bytes,
    private_key: bytes,
    signature_options: str | None = None,
) -> bytes:
    """Sign the provided data using the specified private key and family.

    Args:
        family (str): the cryptographic family to be used for the signing
        data (bytes): the data to sign
        private_key (bytes): the private key to be used for the signing
        signature_options (str): specification code for which
                                signature/verification protocol should be used
    Returns:
        bytes: the signature
    """
    return crypto_modules[family].sign(data, private_key, signature_options)


def verify_signature(
    family: str,
    signature: bytes,
    data: bytes,
    public_key: bytes,
    signature_options: str | None = None,
) -> bool:
    """Verify the given signature of the given data using the given key.

    Args:
        family (str): the cryptographic family to be used for the signature
                    verification
        signature (bytes): the signaure to verify
        data (bytes): the data to sign
        public_key (bytes): the public key to verify the signature against
        signature_options (str): specification code for which
                                signature/verification protocol should be used
    Returns:
        bool: whether or not the signature matches the data
    """
    return crypto_modules[family].verify_signature(
        signature, data, public_key, signature_options
    )


def get_all_families():
    """Get a list of all the cryptography families implemented by this library.

    Returns:
        list: a list of strings, the names of the supported cryptographic
                families
    """
    return [name for name, mod in list(crypto_modules.items())]


def get_encryption_families():
    """Get a list of all the cryptography families implemented by this library
    which support encryption.

    Returns:
        list: a list of strings, the names of the supported cryptographic
                families
    """
    return [
        name
        for name, mod in list(crypto_modules.items())
        if hasattr(mod, "encrypt") and hasattr(mod, "decrypt")
    ]


def get_encrytpion_options(family: str) -> list[str]:
    """Get the encryption options supported by this cryptographic family.
    Args:
        family (str): the name of the cryptographic famliy to query
    Returns:
        list: a list of strings, the supported encryption options
    """
    return crypto_modules[family].get_encrytpion_options()


def get_signature_families():
    """Get a list of all the cryptography families implemented by this library
    which support cryptographic signing.

    Returns:
        list: a list of strings, the names of the supported cryptographic
                families
    """
    return [
        name
        for name, mod in list(crypto_modules.items())
        if hasattr(mod, "sign") and hasattr(mod, "verify_signature")
    ]


def get_signature_options(family):
    """Get the signature options supported by this cryptographic family.
    Args:
        family (str): the name of the cryptographic famliy to query
    Returns:
        list: a list of strings, the supported signature options
    """
    return crypto_modules[family].get_signature_options()

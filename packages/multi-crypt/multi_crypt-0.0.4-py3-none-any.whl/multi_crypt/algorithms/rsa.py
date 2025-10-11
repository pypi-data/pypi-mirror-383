"""Cryptographic applications library based on the RSA algorithm."""
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256, SHA512
from ..errors import EncryptionOptionError, SignatureOptionError

FAMILY_NAME = "RSA"

ENCRYPTION_OPTIONS = [
    "PKCS1_OAEP"
]
SIGNATURE_OPTIONS = [
    "SHA256-PKCS1_15",
    "SHA512-PKCS1_15"
]

DEFAULT_KEY_LENGTH = 2048
DEFAULT_ENCRYPTION_OPTION = "PKCS1_OAEP"
DEFAULT_SIGNATURE_OPTION = "SHA256-PKCS1_15"


def generate_keys(keylength: int = DEFAULT_KEY_LENGTH):
    """Generate a pair of public and private keys.
    Args:
        keylength (int): the number of bits the key is composed of
    Returns:
        tuple: tuple of bytess, a public key and a private key
    """
    if not keylength:
        keylength = DEFAULT_KEY_LENGTH
    key = RSA.generate(keylength)
    public_key = key.publickey().export_key(format='DER')
    private_key = key.export_key(format='DER')

    return (public_key, private_key)


def derive_public_key(private_key: bytes):
    """Given a private key, generate the corresponding public key.
    Args:
        private_key (bytes): the private key
    Returns:
        bytes: the public key
    """
    private_key_obj = RSA.import_key(private_key)
    return private_key_obj.publickey().export_key(format='DER')


def encrypt(
    data_to_encrypt: bytes,
    public_key: bytes,
    encryption_options=DEFAULT_ENCRYPTION_OPTION
):
    """Encrypt the provided data using the specified public key.
    Args:
        data_to_encrypt (bytes): the data to encrypt
        public_key (bytes): the public key to be used for the encryption
        encryption_options (str): specification code for which
                                encryption/decryption protocol should be used
    Returns:
        bytes: the encrypted data
    """
    if not encryption_options:
        encryption_options = DEFAULT_ENCRYPTION_OPTION
    if encryption_options == "PKCS1_OAEP":
        key = RSA.import_key(public_key)
        cipher = PKCS1_OAEP.new(key)
        encrypted_data = cipher.encrypt(data_to_encrypt)
        return encrypted_data
    raise EncryptionOptionError(encryption_options)


def decrypt(
    data_to_decrypt: bytes,
    private_key: bytes,
    encryption_options=DEFAULT_ENCRYPTION_OPTION
):
    """Decrypt the provided data using the specified private key.
    Args:
        data_to_decrypt (bytes): the data to decrypt
        private_key (bytes): the private key to be used for the decryption
        encryption_options (str): specification code for which
                                encryption/decryption protocol should be used
    Returns:
        bytes: the decrypted data
    """
    if not encryption_options:
        encryption_options = DEFAULT_ENCRYPTION_OPTION
    if encryption_options == "PKCS1_OAEP":
        key = RSA.import_key(private_key)
        cipher = PKCS1_OAEP.new(key)
        decrypted_data = cipher.decrypt(data_to_decrypt)
        return decrypted_data
    raise EncryptionOptionError(encryption_options)


def sign(
    data: bytes,
    private_key: bytes,
    signature_options=DEFAULT_SIGNATURE_OPTION
):
    """Sign the provided data using the specified private key.
    Args:
        data (bytes): the data to sign
        private_key (bytes): the private key to be used for the signing
        signature_options (str): specification code for which
                                signature/verification protocol should be used
    Returns:
        bytes: the signature
    """
    if not signature_options:
        signature_options = DEFAULT_SIGNATURE_OPTION
    if signature_options == "SHA256-PKCS1_15":
        key = RSA.import_key(private_key)
        data_hash = SHA256.new(data)
        signature = pkcs1_15.new(key).sign(data_hash)
        return signature
    if signature_options == "SHA512-PKCS1_15":
        key = RSA.import_key(private_key)
        data_hash = SHA512.new(data)
        signature = pkcs1_15.new(key).sign(data_hash)
        return signature
    raise SignatureOptionError(signature_options)


def verify_signature(
        signature: bytes,
        data: bytes,
        public_key: bytes,
        signature_options=DEFAULT_SIGNATURE_OPTION):
    """Verify the provided signature of the provided data using the specified
    private key.
    Args:
        signature (bytes): the signaure to verify
        data (bytes): the data to sign
        public_key (bytes): the public key to verify the signature against
        signature_options (str): specification code for which
                                signature/verification protocol should be used
    Returns:
        bool: whether or not the signature matches the data
    """
    if not signature_options:
        signature_options = DEFAULT_SIGNATURE_OPTION
    if signature_options == "SHA256-PKCS1_15":
        key = RSA.import_key(public_key)
        data_hash = SHA256.new(data)
        try:
            pkcs1_15.new(key).verify(data_hash, signature)
            return True
        except (ValueError, TypeError):
            return False
    if signature_options == "SHA512-PKCS1_15":
        key = RSA.import_key(public_key)
        data_hash = SHA512.new(data)
        try:
            pkcs1_15.new(key).verify(data_hash, signature)
            return True
        except (ValueError, TypeError):
            return False
    raise SignatureOptionError(signature_options)


def get_encrytpion_options():
    """Get the encryption options supported by this cryptographic family.
    Returns:
        list: a list of strings, the supported encryption options
    """
    return ENCRYPTION_OPTIONS


def get_signature_options():
    """Get the signature options supported by this cryptographic family.
    Returns:
        list: a list of strings, the supported signature options
    """
    return SIGNATURE_OPTIONS

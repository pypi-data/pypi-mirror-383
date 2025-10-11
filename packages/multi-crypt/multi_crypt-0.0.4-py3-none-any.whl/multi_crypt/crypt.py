"""This module contains Crypt, a class that enables an object-oriented approach
to working with cryptography.
For a functional approach, use multicrypt, with Crypt is based on.
Crypt implements all the functionality of multi_crypt.
"""

from typing import Type, TypeVar

from .multi_crypt import (  # pylint:disable=unused-import
    decrypt,
    derive_public_key,
    encrypt,
    generate_keys,
    get_encrytpion_options,
    get_signature_options,
    sign,
    verify_signature,
)
from .utils import to_bytes

_Crypt = TypeVar("_Crypt", bound="Crypt")


class Crypt:
    """An object for performing various cryptographic operations.

    It provides public and private key generation & verification,
    encryption & decryption and signing & signature-verification functionality.
    If can even be used if only a public key is provided, limiting it to only
    encryption and signature verification, but can of course be unlocked from
    this state to enable full functionality.
    """

    public_key: bytes
    private_key: bytes | None

    def __init__(
        self,
        family: str,
        private_key: bytes | None = None,
        public_key: bytes | None = None,
    ):
        """Create a Crypt object for an existing set of cryptographic keys.

        To create a Crypt with newly generated keys, use `Crypt.new()`
        Supplying a private key will enable all cryptographic operations,
        supplying a public key only will enable only encryption and signature
        verification.

        Args:
            family (str): the cryptographic family of the keys
            private_key (bytes): the private key. Required for the ability
                                    to decrypt and sign data
            public_key (bytes): the public key. Not required if private_key
                                    is supplied
        Returns:
            Crypt: Crypt object for performing cryptographic operations
        """
        self.family = family
        if private_key:
            # type checking private key
            self.private_key = to_bytes(private_key, "private_key")
            self.public_key = derive_public_key(self.family, self.private_key)
        else:
            self.private_key = None
        if public_key:
            public_key = to_bytes(public_key, "private_key")
            if private_key:
                if not self.public_key == public_key:
                    raise KeyMismatchError()
            self.public_key = public_key
        elif not private_key:
            raise ValueError(
                "Either private_key or public_key must be supplied."
            )

    @classmethod
    def new(
        cls: Type[_Crypt], family: str, keylength: int | None = None
    ) -> _Crypt:
        """Create a Crypt from newly generated of public and private keys.

        Args:
            family (str): the cryptographic family of the keys
            keylength (int): the number of bits the key is composed of
        Returns:
            Crypt: Crypt object for performing cryptographic operations
        """
        # pylint: disable=unused-variable
        public_key, private_key = generate_keys(
            family=family, keylength=keylength
        )
        return cls(family, private_key)

    def serialise_private(self) -> dict:
        """Serialise all this crypt's information including its private key."""
        if not self.private_key:
            raise LockedError()
        return {
            "family": self.family,
            "private_key": self.private_key.hex(),
            "public_key": self.public_key.hex(),
        }

    def serialise_public(self) -> dict:
        """Serialise this crypt's information, excluding its private key."""
        return {
            "family": self.family,
            "public_key": self.public_key.hex(),
        }

    @classmethod
    def deserialise(cls: Type[_Crypt], data: dict) -> _Crypt:
        """Load a Crypt object from serialised data."""
        return cls(
            family=data["family"],
            private_key=data.get("private_key"),
            public_key=data["public_key"],
        )

    def unlock(self, private_key: bytes | bytearray | str) -> None:
        """Unlock the Crypt with a private key.

        Args:
            private_key (bytes): the private key corresponding to this
                                    Crypt's public key
        """
        # type checking private key
        private_key = to_bytes(private_key, "private_key")

        if derive_public_key(self.family, private_key) != self.public_key:
            raise KeyMismatchError(
                (
                    "Wrong private key! The given private key does not match this "
                    "encryptor's public key."
                )
            )
        self.private_key = private_key

    def encrypt(
        self, data_to_encrypt: bytes, encryption_options: str | None = None
    ) -> bytes:
        """Encrypt the provided data using the specified public key.

        Args:
            data_to_encrypt (bytes): the data to encrypt
            encryption_options (str): specification code for which
                                    encryption/decryption protocol should be used
        Returns:
            bytes: the encrypted data
        """
        return encrypt(
            self.family,
            data_to_encrypt,
            self.public_key,
            encryption_options=encryption_options,
        )

    def decrypt(
        self, encrypted_data: bytes, encryption_options: str | None = None
    ) -> bytes:
        """Decrypt the provided data using the specified private key.

        Args:
            encrypted_data (bytes): the data to decrypt
            encryption_options (str): specification code for which
                                    encryption/decryption protocol should be used
        Returns:
            bytes: the decrypted data
        """
        if not self.private_key:
            raise LockedError()
        return decrypt(
            self.family,
            encrypted_data,
            self.private_key,
            encryption_options=encryption_options,
        )

    def sign(self, data: bytes, signature_options: str | None = None) -> bytes:
        """Sign the provided data using the specified private key.

        Args:
            data (bytes): the data to sign
            private_key (bytes): the private key to be used for the signing
            signature_options (str): specification code for which
                                signature/verification protocol should be used
        Returns:
            bytes: the signature
        """
        if not self.private_key:
            raise LockedError()
        return sign(
            self.family,
            to_bytes(data, "data"),
            self.private_key,
            signature_options=signature_options,
        )

    def verify_signature(
        self,
        signature: bytes,
        data: bytes,
        signature_options: str | None = None,
    ) -> bool:
        """Verify the given signature of the given data using the given key.

        Args:
            signature (bytes): the signaure to verify
            data (bytes): the data to sign
            public_key (bytes): the public key to verify the signature against
            signature_options (str): specification code for which
                                signature/verification protocol should be used
        Returns:
            bool: whether or not the signature matches the data
        """
        return verify_signature(
            self.family,
            to_bytes(signature, "signature"),
            to_bytes(data, "data"),
            self.public_key,
            signature_options=signature_options,
        )

    def get_private_key(self) -> bytes:
        """Get the private key as bytes."""
        if not self.private_key:
            raise LockedError()
        return self.private_key

    def get_public_key(self) -> bytes:
        """Get the private key as bytes."""
        return self.public_key

    def get_private_key_str(self) -> str:
        """Get the private key as a string."""
        if not self.private_key:
            raise LockedError()
        return self.private_key.hex()

    def get_public_key_str(self) -> str:
        """Get the private key as a string."""
        return self.public_key.hex()

    def get_encrytpion_options(self) -> list[str]:
        """Get the encryption options supported by this cryptographic family.

        Args:
            family (str): the name of the cryptographic famliy to query
        Returns:
            list: a list of strings, the supported encryption options
        """
        return get_encrytpion_options(self.family)

    def get_signature_options(self) -> list[str]:
        """Get the signature options supported by this cryptographic family.

        Args:
            family (str): the name of the cryptographic famliy to query
        Returns:
            list: a list of strings, the supported signature options
        """
        return get_signature_options(self.family)


class LockedError(Exception):
    """When private-key operations are attempted with a locked object."""

    def __str__(self) -> str:
        """Print this Exception's message."""
        return (
            "This Crypt is locked. "
            "Unlock with Encryptor.unlock() in order to decrypt and sign data."
        )


class KeyMismatchError(Exception):
    """When non-corresponding public and private keys are supplied."""

    def_message = "This supplied private and public keys don't match."

    def __init__(self, message=def_message):
        super().__init__()
        self.message = message

    def __str__(self) -> str:
        """Print this Exception's message."""
        return self.message

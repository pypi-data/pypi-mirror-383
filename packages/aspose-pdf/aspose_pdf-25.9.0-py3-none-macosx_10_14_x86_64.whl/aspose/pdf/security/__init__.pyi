﻿import aspose.pdf
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class CertificateEncryptionOptions:
    '''Represents a class for encrypting options a PDF document using a certificate-based encryption method.
    Used to open encrypted PDF documents.'''
    
    @overload
    def __init__(self, public_certificate_path: str, pfx_path: str, pfx_password: str):
        '''Creates an instance of :class:`CertificateEncryptionOptions` class.
        
        :param public_certificate_path: The public certificate file path.
        :param pfx_path: The p12 archive file path.
        :param pfx_password: The p12 archive file password.'''
        ...
    
    @overload
    def __init__(self, public_certificate, pfx_path: str, pfx_password: str):
        '''Creates an instance of :class:`CertificateEncryptionOptions` class.
        
        :param public_certificate: The public certificate.
        :param pfx_path: The p12 archive file path.
        :param pfx_password: The p12 archive file password.'''
        ...
    
    ...

class DsaAlgorithmInfo(aspose.pdf.security.KeyedSignatureAlgorithmInfo):
    '''Represents a class for the information about the DSA signature algorithm.'''
    
    ...

class EcdsaAlgorithmInfo(aspose.pdf.security.KeyedSignatureAlgorithmInfo):
    '''Represents a class for the information about the ECDSA signature algorithm.'''
    
    @property
    def ECC_NAME(self) -> str:
        '''Gets the name of the elliptic curve used by the ECDSA.'''
        ...
    
    ...

class EncryptionParameters:
    '''Represents an encryption parameters class.'''
    
    def __init__(self):
        ...
    
    @property
    def filter(self) -> str:
        '''Gets the filter name.'''
        ...
    
    @property
    def sub_filter(self) -> str:
        '''Gets the sub-filter name.'''
        ...
    
    @property
    def password(self) -> str:
        '''Gets the password from input.'''
        ...
    
    @property
    def permissions(self) -> aspose.pdf.Permissions:
        '''The document permissions.'''
        ...
    
    @property
    def permissions_int(self) -> int:
        '''The integer representation of document permissions.'''
        ...
    
    @property
    def version(self) -> int:
        '''Gets the handler or encryption algorithm version.'''
        ...
    
    @property
    def key_length(self) -> int:
        '''Gets the key length.'''
        ...
    
    @property
    def user_key(self) -> bytes:
        '''Gets the user key (The "U" field of encryption dictionary.)'''
        ...
    
    @property
    def owner_key(self) -> bytes:
        '''Gets the owner key(The "O" field of encryption dictionary.)'''
        ...
    
    @property
    def revision(self) -> int:
        '''Gets the handler or encryption algorithm revision.'''
        ...
    
    @property
    def perms(self) -> bytes:
        '''Gets the Perms field data.
        It is an encrypted permissions.'''
        ...
    
    ...

class ICustomSecurityHandler:
    '''The custom security handler interface.'''
    
    def encrypt_permissions(self, permissions: int) -> bytes:
        '''Encrypt the document's permissions field. The result will be written to the Perms encryption dictionary field.
        When opening a document, the value can be obtained in :class:`EncryptionParameters` via the Perms field.
        Allows you to check if the document permissions have changed.
        
        :param permissions: The document permissions in integer representation.
        :returns: The encrypted array.'''
        ...
    
    def get_owner_key(self, user_password: str, owner_password: str) -> bytes:
        '''Creates an encoded array based on passwords that will be written to the O field of the encryption dictionary.
        Should only rely on the arguments passed. The user password can be calculated from this field using the owner password.
        Called during encryption to prepare it and populate the encryption dictionary.
        The value will be available in :meth:`ICustomSecurityHandler.calculate_encryption_key` to get the key from the UserKey.
        The passwords specified by the user when calling document encryption will be passed.
        Passwords may not be specified or only one may be specified.
        
        :param user_password: The user password.
        :param owner_password: The owner password.
        :returns: The array of owner key.'''
        ...
    
    def get_user_key(self, user_password: str) -> bytes:
        '''Creates an encoded array based on the user's password.
        This value is typically used to check if the password belongs to the user or owner, and to get the encryption key.
        Called during encryption to prepare it and populate the encryption dict.
        The user-specified password is passed as an argument when calling document encryption.
        
        :param user_password: The user password.
        :returns: The array of user key.'''
        ...
    
    def initialize(self, parameters: aspose.pdf.security.EncryptionParameters) -> None:
        '''Called to initialize the current instance for encryption.
        Note that when encrypting, it will be filled with the data of the transferred properties :class:`ICustomSecurityHandler`, and when opening the document from the encryption dictionary.
        If the method is called during new encryption, then :attr:`EncryptionParameters.user_key` and :attr:`EncryptionParameters.owner_key` will be null.
        
        :param parameters: The encryption parameters.'''
        ...
    
    def calculate_encryption_key(self, password: str) -> bytes:
        '''Calculate the EncryptionKey. Generally the key is calculated based on the UserKey.
        You can use values from EncryptionParams, which contains the current parameters at the time of the call.
        This value is passed as the key argument in :meth:`ICustomSecurityHandler.encrypt` and :meth:`ICustomSecurityHandler.decrypt`.
        
        :param password: Password entered by the user.
        :returns: The array of encryption key.'''
        ...
    
    def encrypt(self, data: bytes, object_number: int, generation: int, key: bytes) -> bytes:
        '''Encrypt the data array.
        
        :param data: Data to encrypt.
        :param object_number: Number of the object containing the encrypted data.
        :param generation: Generation of the object.
        :param key: Key obtained by the CalculateEncryptionKey method
        :returns: The encrypted data.'''
        ...
    
    def decrypt(self, data: bytes, object_number: int, generation: int, key: bytes) -> bytes:
        '''Decrypt the data array.
        
        :param data: Data to decrypt.
        :param object_number: Number of the object containing the encrypted data.
        :param generation: Generation of the object.
        :param key: Key obtained by the CalculateEncryptionKey method
        :returns: The decrypted data.'''
        ...
    
    def is_owner_password(self, password: str) -> bool:
        '''Check if the password is the document owner's password.
        The method is called after Initialize. The method call is used in the PDF API.
        
        :param password: The password.
        :returns: True, if it is an owner password.'''
        ...
    
    def is_user_password(self, password: str) -> bool:
        '''Check if the password belongs to the user (password for opening the document).
        The method is called after Initialize. The method call is used in the PDF API.
        
        :param password: The password.
        :returns: True, if it is a password for opening the document.'''
        ...
    
    @property
    def filter(self) -> str:
        '''Gets the filter name.'''
        ...
    
    @property
    def sub_filter(self) -> str:
        '''Gets the sub-filter name.'''
        ...
    
    @property
    def version(self) -> int:
        '''Gets the handler or encryption algorithm version.'''
        ...
    
    @property
    def revision(self) -> int:
        '''Gets the handler or encryption algorithm revision.'''
        ...
    
    @property
    def key_length(self) -> int:
        '''Gets the key length.'''
        ...
    
    ...

class KeyedSignatureAlgorithmInfo(aspose.pdf.security.SignatureAlgorithmInfo):
    '''Represents a class for information about a keyed signature algorithm.'''
    
    @property
    def KEY_SIZE(self) -> int:
        '''Gets the size of the cryptographic key used by the signature algorithm.'''
        ...
    
    ...

class RsaAlgorithmInfo(aspose.pdf.security.KeyedSignatureAlgorithmInfo):
    '''Represents a class for the information about the RSA signature algorithm.'''
    
    ...

class SignatureAlgorithmInfo:
    '''Represents a class for information about a signature algorithm, including its type,
    cryptographic standard, and digest hash algorithm.'''
    
    @property
    def signature_name(self) -> str:
        '''Gets the name of the signature field.'''
        ...
    
    @property
    def ALGORITHM_TYPE(self) -> aspose.pdf.security.SignatureAlgorithmType:
        '''Gets the type of the signature algorithm used for signing the PDF document.'''
        ...
    
    @property
    def CRYPTOGRAPHIC_STANDARD(self) -> aspose.pdf.security.CryptographicStandard:
        '''Gets the cryptographic standard used for signing the PDF document.'''
        ...
    
    @property
    def DIGEST_HASH_ALGORITHM(self) -> aspose.pdf.DigestHashAlgorithm:
        '''Gets the digest hash algorithm used for the signature.
        For a timestamp, this is the digest hash algorithm with which the hash of the document content is signed.'''
        ...
    
    ...

class SignatureLengthMismatchException(aspose.pdf.PdfException):
    '''Represents errors that occur during PDF signing.
    Occurs if Aspose.Pdf.Forms.SignHash is used to sign a document and the actual length of the signature is greater than that specified in the :attr:`aspose.pdf.forms.Signature.default_signature_length` option.'''
    
    ...

class TimestampAlgorithmInfo(aspose.pdf.security.SignatureAlgorithmInfo):
    '''Represents a class for the information about the timestamp signature algorithm.'''
    
    @property
    def CONTENT_HASH_ALGORITHM(self) -> aspose.pdf.DigestHashAlgorithm:
        '''Gets the hash algorithm that hashed the content of the document and then signed it using :attr:`SignatureAlgorithmInfo.DIGEST_HASH_ALGORITHM`.'''
        ...
    
    ...

class UnknownSignatureAlgorithmInfo(aspose.pdf.security.SignatureAlgorithmInfo):
    '''Represents a class for the unknown signature algorithm information.'''
    
    ...

class ValidationOptions:
    '''Represents options for validating a digital signature in a PDF document.'''
    
    def __init__(self):
        ...
    
    @property
    def validation_mode(self) -> aspose.pdf.security.ValidationMode:
        '''Gets or sets the mode of validation for digital signatures in a PDF document.
        The ValidationMode property determines the strictness of the validation process.'''
        ...
    
    @validation_mode.setter
    def validation_mode(self, value: aspose.pdf.security.ValidationMode):
        ...
    
    @property
    def validation_method(self) -> aspose.pdf.security.ValidationMethod:
        '''Gets or sets the method used to validate a certificate.'''
        ...
    
    @validation_method.setter
    def validation_method(self, value: aspose.pdf.security.ValidationMethod):
        ...
    
    @property
    def request_timeout(self) -> int:
        '''Gets or sets the timeout duration, in milliseconds, for network-related operations during the validation process.
        The RequestTimeout property defines the maximum time the system should wait for a network response
        when accessing online resources, such as revocation status or OCSP servers.'''
        ...
    
    @request_timeout.setter
    def request_timeout(self, value: int):
        ...

    @property
    def check_certificate_chain(self) -> bool:
        '''Gets or sets a value indicating whether the certificate chain
        should be checked during the validation process.
        
        When the property is set, the existence of a chain of certificates will be checked,
        if it is absent, then the result of the verification will be :attr:`ValidationStatus.UNDEFINED`, which corresponds to the behavior of Adobe Acrobat.
        If you just want to check the status of revocation online, then set the field in false.
        The default value is false.'''
        ...
    
    @check_certificate_chain.setter
    def check_certificate_chain(self, value: bool):
        ...
    
    ...

class ValidationResult:
    '''Represents the result of a validation process for a certificate.
    
    The ValidationResult class provides information about the outcome of validating a certificate,
    including its status and a message describing any issues encountered during the validation.'''
    
    @property
    def status(self) -> aspose.pdf.security.ValidationStatus:
        '''Gets the status of the validation process for a certificate.
        
        The Status property indicates the outcome of the certificate validation.
        Possible values are defined in the :class:`ValidationStatus` enumeration,
        such as Valid, Invalid, or Undefined. It provides an insight into whether
        the certificate passed the validation checks or not.'''
        ...
    
    @property
    def message(self) -> str:
        '''Represents the message associated with the validation result.
        
        The Message property provides additional context or information about
        the state of the validation result.'''
        ...
    
    ...

class CryptographicStandard:
    '''Represents the available cryptographic standards for securing PDF documents.'''
    
    PKCS1: CryptographicStandard
    PKCS7: CryptographicStandard
    RFC3161: CryptographicStandard

class SignatureAlgorithmType:
    '''Enumerates the types of signature algorithms used for digital signatures.'''
    
    ECDSA: SignatureAlgorithmType
    RSA: SignatureAlgorithmType
    DSA: SignatureAlgorithmType
    TIMESTAMP: SignatureAlgorithmType
    UNKNOWN: SignatureAlgorithmType

class ValidationMethod:
    '''Represents an enum  defined the method used for certificate validation.'''
    
    AUTO: ValidationMethod
    OCSP: ValidationMethod
    CRL: ValidationMethod
    ALL: ValidationMethod

class ValidationMode:
    '''Specifies the validation mode for PDF signature validation processes.'''
    
    NONE: ValidationMode
    ONLY_CHECK: ValidationMode
    STRICT: ValidationMode

class ValidationStatus:
    '''Represents the validation status of a certificate validation.
    
    This enumeration defines the possible outcomes of certificate validation:
    - Valid: Indicates that the certificate has been successfully validated.
    - Invalid: Indicates that the certificate validation failed.
    - Undefined: Indicates that the validation process was inconclusive or not performed.'''
    
    VALID: ValidationStatus
    INVALID: ValidationStatus
    UNDEFINED: ValidationStatus


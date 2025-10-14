﻿import aspose.pdf
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class CompromiseCheckResult:
    '''Represents a class for checking document digital signatures for compromise.'''
    
    @property
    def has_compromised_signatures(self) -> bool:
        '''Indicates whether there are any compromised digital signatures in the document.
        Returns True if at least one signature is compromised; otherwise, False.'''
        ...
    
    @property
    def signatures_coverage(self) -> aspose.pdf.signatures.SignaturesCoverage:
        '''Gets the coverage state of digital signatures in a document.
        If it is equal to :attr:`SignaturesCoverage.UNDEFINED`, then one of the signatures is compromised.'''
        ...
    
    @property
    def COMPROMISED_SIGNATURES(self) -> list[aspose.pdf.facades.SignatureName]:
        '''Gets a collection of digital signatures that have been identified as compromised.
        This property contains the list of all compromised signatures detected in the document.'''
        ...
    
    ...

class SignaturesCoverage:
    '''Represents enum for the level of coverage provided by digital signatures in a document.'''
    
    UNDEFINED: SignaturesCoverage
    ENTIRELY_SIGNED: SignaturesCoverage
    PARTIALLY_SIGNED: SignaturesCoverage


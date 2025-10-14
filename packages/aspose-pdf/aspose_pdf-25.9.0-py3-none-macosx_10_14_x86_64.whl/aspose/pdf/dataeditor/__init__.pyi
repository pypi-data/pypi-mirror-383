﻿import aspose.pdf
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class CosPdfBoolean(aspose.pdf.dataeditor.CosPdfPrimitive):
    '''This class represents boolean type.'''
    
    def __init__(self, value: bool):
        '''Initializes a new instance of the Aspose.Pdf.Engine.Data.PdfBoolean class.
        
        :param value: if set to ``True`` [value].'''
        ...
    
    def to_cos_pdf_boolean(self) -> aspose.pdf.dataeditor.CosPdfBoolean:
        '''Tries cast this instance to :class:`CosPdfBoolean`.
        
        :returns: null if instance is not :class:`CosPdfBoolean` else :class:`CosPdfBoolean`.'''
        ...
    
    @property
    def value(self) -> bool:
        '''Gets the value.'''
        ...
    
    ...

class CosPdfDictionary(aspose.pdf.dataeditor.CosPdfPrimitive):
    '''A class for accessing an object's dictionary.'''
    
    def __init__(self, resources: aspose.pdf.Resources):
        '''Creates a dictionary from resources.
        
        :param resources: Resources with a dictionary for work.
        :raises System.ArgumentNullException: The resources are null.'''
        ...
    
    @overload
    @staticmethod
    def create_empty_dictionary(self, page: aspose.pdf.Page) -> aspose.pdf.dataeditor.CosPdfDictionary:
        '''Creates an empty dictionary that will be attached to the page.
        
        :param page: Result dictionary will be attached to this page.
        :raises System.ArgumentNullException: The page is null.
        :returns: An empty dictionary.'''
        ...
    
    @overload
    @staticmethod
    def create_empty_dictionary(self, document: aspose.pdf.Document) -> aspose.pdf.dataeditor.CosPdfDictionary:
        '''Creates an empty dictionary that will be attached to the document.
        
        :param document: Result dictionary will be attached to this document.
        :raises System.ArgumentNullException: The document is null.
        :returns: An empty dictionary.'''
        ...
    
    def to_cos_pdf_dictionary(self) -> aspose.pdf.dataeditor.CosPdfDictionary:
        '''Tries cast this instance to :class:`CosPdfDictionary`.
        
        :returns: null if instance is not :class:`CosPdfDictionary` else :class:`CosPdfDictionary`.'''
        ...
    
    def contains_key(self, key: str) -> bool:
        '''Determines whether the :class:`CosPdfDictionary` contains an element with the specified key.
        
        :param key: The key to locate in the  :class:`CosPdfDictionary`.
        :returns: true if the :class:`CosPdfDictionary` contains an editable element with the key; otherwise, false.'''
        ...
    
    def remove(self, key: str) -> bool:
        '''Removes the element with the specified key from the :class:`CosPdfDictionary`.
        
        :param key: The key of the element to remove.
        :returns: True if the element is successfully removed; otherwise, false.
                  This method also returns false if key was not found in the original dictionary or key the key is not editable'''
        ...
    
    def try_get_value(self, key: str, value) -> bool:
        '''For access to simple data type like string, name, bool, number.
        Returns null for other types.
        
        :param key: Key value
        :param value: returns :class:`ICosPdfPrimitive` for key or null.
        :returns: Returns true if :class:`ICosPdfPrimitive` is like string, name, bool, number.
                  Returns false for all other types.'''
        ...
    
    def add(self, key: str, value: aspose.pdf.dataeditor.ICosPdfPrimitive) -> None:
        '''Set :class:`ICosPdfPrimitive` to dictionary.
        
        :param key: Key.
        :param value: Value.
        :raises System.ArgumentException: Throw exception if key/value can't be edited or removed.'''
        ...
    
    def clear(self) -> None:
        '''Removes all items from the :class:`CosPdfDictionary`.'''
        ...
    
    @property
    def all_keys(self) -> None:
        '''Full collection of keys.
        Contains editable and not editable keys.'''
        ...
    
    @property
    def keys(self) -> None:
        '''Collection of editable keys.'''
        ...
    
    @property
    def values(self) -> None:
        '''Gets an System.Collections.ICollection containing the values in the :class:`CosPdfDictionary`.'''
        ...
    
    @property
    def count(self) -> int:
        '''Gets the number of elements contained in the :class:`CosPdfDictionary`.'''
        ...
    
    @property
    def is_read_only(self) -> bool:
        '''Gets a value indicating whether the :class:`CosPdfDictionary` is read-only.
        
        :returns: true if the :class:`CosPdfDictionary` is read-only; otherwise, false.'''
        ...
    
    ...

class CosPdfName(aspose.pdf.dataeditor.CosPdfPrimitive):
    '''This class represents Pdf Name object.'''
    
    def __init__(self, value: str):
        '''Initializes a new instance of the :class:`CosPdfName` class.
        
        :param value: The name.'''
        ...
    
    def to_cos_pdf_name(self) -> aspose.pdf.dataeditor.CosPdfName:
        '''Tries cast this instance to :class:`CosPdfName`.
        
        :returns: null if instance is not :class:`CosPdfName` else :class:`CosPdfName`.'''
        ...
    
    @property
    def value(self) -> str:
        '''Gets the value.'''
        ...
    
    ...

class CosPdfNumber(aspose.pdf.dataeditor.CosPdfPrimitive):
    '''This class represents Pdf Number type.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the :class:`CosPdfNumber` class.'''
        ...
    
    @overload
    def __init__(self, value: float):
        '''Initializes a new instance of the :class:`CosPdfNumber` class.
        
        :param value: The number.'''
        ...
    
    def to_cos_pdf_number(self) -> aspose.pdf.dataeditor.CosPdfNumber:
        '''Tries cast this instance to :class:`CosPdfNumber`.
        
        :returns: null if instance is not :class:`CosPdfNumber` else :class:`CosPdfNumber`.'''
        ...
    
    @property
    def value(self) -> float:
        '''Gets the value.'''
        ...
    
    ...

class CosPdfPrimitive:
    '''This class represents base public type :class:`CosPdfPrimitive`.'''
    
    def to_cos_pdf_number(self) -> aspose.pdf.dataeditor.CosPdfNumber:
        '''Tries cast this instance to :class:`CosPdfNumber`.
        
        :returns: null if instance is not :class:`CosPdfNumber` else :class:`CosPdfNumber`.'''
        ...
    
    def to_cos_pdf_name(self) -> aspose.pdf.dataeditor.CosPdfName:
        '''Tries cast this instance to :class:`CosPdfName`.
        
        :returns: null if instance is not :class:`CosPdfName` else :class:`CosPdfName`.'''
        ...
    
    def to_cos_pdf_string(self) -> aspose.pdf.dataeditor.CosPdfString:
        '''Tries cast this instance to :class:`CosPdfString`.
        
        :returns: null if instance is not :class:`CosPdfString` else :class:`CosPdfString`.'''
        ...
    
    def to_cos_pdf_boolean(self) -> aspose.pdf.dataeditor.CosPdfBoolean:
        '''Tries cast this instance to :class:`CosPdfBoolean`.
        
        :returns: null if instance is not :class:`CosPdfBoolean` else :class:`CosPdfBoolean`.'''
        ...
    
    def to_cos_pdf_dictionary(self) -> aspose.pdf.dataeditor.CosPdfDictionary:
        '''Tries cast this instance to :class:`CosPdfDictionary`.
        
        :returns: null if instance is not :class:`CosPdfDictionary` else :class:`CosPdfDictionary`.'''
        ...
    
    ...

class CosPdfString(aspose.pdf.dataeditor.CosPdfPrimitive):
    '''This class represents Pdf String object.'''
    
    @overload
    def __init__(self, value: str):
        '''Initializes a new instance of the :class:`CosPdfString` class.
        
        :param value: The value.'''
        ...
    
    @overload
    def __init__(self, value: str, is_hexadecimal: bool):
        '''Initializes a new instance of the :class:`CosPdfString` class.
        
        :param value: The string.
        :param is_hexadecimal: if set to ``True`` [is hexadecimal].'''
        ...
    
    def to_cos_pdf_string(self) -> aspose.pdf.dataeditor.CosPdfString:
        '''Tries cast this instance to :class:`CosPdfString`.
        
        :returns: null if instance is not :class:`CosPdfString` else :class:`CosPdfString`.'''
        ...
    
    @property
    def is_hexadecimal(self) -> bool:
        '''Gets a value indicating whether this instance is hexadecimal.'''
        ...
    
    @property
    def value(self) -> str:
        '''Gets the string (ANSII).'''
        ...
    
    ...

class DictionaryEditor:
    '''A class for accessing an document's tree dictionary (document dictionary, page dictionary, resources dictionary).'''
    
    @overload
    def __init__(self, page: aspose.pdf.Page):
        ''':param page: A page with a dictionary for work.
        :raises System.ArgumentNullException: The page is null or page structure is broken.'''
        ...
    
    @overload
    def __init__(self, document: aspose.pdf.Document):
        ''':param document: A document with a dictionary for work.
        :raises System.ArgumentNullException: The document is null.'''
        ...
    
    @overload
    def __init__(self, resources: aspose.pdf.Resources):
        ''':param resources: Resources with a dictionary for work.
        :raises System.ArgumentNullException: The resources are null.'''
        ...
    
    def contains_key(self, key: str) -> bool:
        '''Determines whether the :class:`DictionaryEditor` contains an element with the specified key.
        
        :param key: The key to locate in the  :class:`DictionaryEditor`.
        :returns: true if the :class:`DictionaryEditor` contains an editable element with the key; otherwise, false.'''
        ...
    
    def remove(self, key: str) -> bool:
        '''Removes the element with the specified key from the :class:`DictionaryEditor`.
        
        :param key: The key of the element to remove.
        :returns: True if the element is successfully removed; otherwise, false.
                  This method also returns false if key was not found in the original dictionary or key the key is not editable'''
        ...
    
    def try_get_value(self, key: str, value) -> bool:
        '''For access to simple data type like string, name, bool, number.
        Returns null for other types.
        
        :param key: Key value
        :param value: returns :class:`ICosPdfPrimitive` for key or null.
        :returns: Returns true if :class:`ICosPdfPrimitive` is like string, name, bool, number.
                  Returns false for all other types.'''
        ...
    
    def add(self, key: str, value: aspose.pdf.dataeditor.ICosPdfPrimitive) -> None:
        '''Set :class:`ICosPdfPrimitive` to dictionary.
        
        :param key: Key.
        :param value: Value.
        :raises System.ArgumentException: Throw exception if key/value can't be edited or removed.'''
        ...
    
    def clear(self) -> None:
        '''Removes all items from the :class:`DictionaryEditor`.'''
        ...
    
    @property
    def all_keys(self) -> None:
        '''Full collection of keys.
        Contains editable and not editable keys.'''
        ...
    
    @property
    def keys(self) -> None:
        '''Collection of editable keys.'''
        ...
    
    @property
    def values(self) -> None:
        '''Gets an System.Collections.ICollection containing the values in the :class:`DictionaryEditor`.'''
        ...
    
    @property
    def count(self) -> int:
        '''Gets the number of elements contained in the :class:`DictionaryEditor`.'''
        ...
    
    @property
    def is_read_only(self) -> bool:
        '''Gets a value indicating whether the :class:`DictionaryEditor` is read-only.
        
        :returns: true if the :class:`DictionaryEditor` is read-only; otherwise, false.'''
        ...
    
    ...

class ICosPdfPrimitive:
    '''Interface for work with PDF data entity'''
    
    def to_cos_pdf_name(self) -> aspose.pdf.dataeditor.CosPdfName:
        '''Tries cast this instance to :class:`CosPdfName`.
        
        :returns: null if instance is not :class:`CosPdfName` else :class:`CosPdfName`.'''
        ...
    
    def to_cos_pdf_string(self) -> aspose.pdf.dataeditor.CosPdfString:
        '''Tries cast this instance to :class:`CosPdfString`.
        
        :returns: null if instance is not :class:`CosPdfString` else :class:`CosPdfString`.'''
        ...
    
    def to_cos_pdf_boolean(self) -> aspose.pdf.dataeditor.CosPdfBoolean:
        '''Tries cast this instance to :class:`CosPdfBoolean`.
        
        :returns: null if instance is not :class:`CosPdfBoolean` else :class:`CosPdfBoolean`.'''
        ...
    
    def to_cos_pdf_number(self) -> aspose.pdf.dataeditor.CosPdfNumber:
        '''Tries cast this instance to :class:`CosPdfNumber`.
        
        :returns: null if instance is not :class:`CosPdfNumber` else :class:`CosPdfNumber`.'''
        ...
    
    def to_cos_pdf_dictionary(self) -> aspose.pdf.dataeditor.CosPdfDictionary:
        '''Tries cast this instance to :class:`CosPdfDictionary`.
        
        :returns: null if instance is not :class:`CosPdfDictionary` else :class:`CosPdfDictionary`.'''
        ...
    
    def to_string(self) -> str:
        '''System.String representation of instance :class:`ICosPdfPrimitive`.
        
        :returns: Value of System.String representation of instance :class:`ICosPdfPrimitive`.'''
        ...
    
    ...


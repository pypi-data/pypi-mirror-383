﻿import aspose.pdf
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class IStructureRecognitionVisitor:
    
    def start_document(self) -> None:
        '''Signals the start of document processing.'''
        ...
    
    def end_document(self) -> None:
        '''Signals the end of document processing.'''
        ...
    
    def visit_table(self, table: aspose.pdf.Table) -> None:
        '''Visits a recognized table in the document structure.
        
        :param table: The table element to process.'''
        ...
    
    def visit_section_end(self, margin_info: aspose.pdf.MarginInfo) -> None:
        '''Visits the end of a recognized section in the document.
        
        :param margin_info: The margin information for the section.'''
        ...
    
    def visit_paragraph(self, paragraph: aspose.pdf.BaseParagraph) -> None:
        '''Visits a recognized paragraph in the document structure.
        
        :param paragraph: The paragraph element to process.'''
        ...
    
    ...

class StructureRecognitionVisitor:
    
    def __init__(self):
        ...
    
    @overload
    def recognize(self, document: aspose.pdf.Document) -> None:
        ...
    
    @overload
    def recognize(self, page: aspose.pdf.Page) -> None:
        ...
    
    ...


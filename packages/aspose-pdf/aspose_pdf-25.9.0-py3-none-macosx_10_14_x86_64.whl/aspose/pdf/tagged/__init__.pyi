﻿import aspose.pdf
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class IAdjustPosition:
    '''Interface for positioning methods.'''
    
    def adjust_position(self, position_settings: aspose.pdf.tagged.PositionSettings) -> None:
        '''Adjust position.
        
        :param position_settings: Position settings'''
        ...
    
    ...

class ITaggedContent:
    '''Represents interface for work with TaggedPdf content of document.'''
    
    @overload
    def create_header_element(self) -> aspose.pdf.logicalstructure.HeaderElement:
        '''Creates :class:`aspose.pdf.logicalstructure.HeaderElement`.
        
        :returns: Created structure element.'''
        ...
    
    @overload
    def create_header_element(self, level: int) -> aspose.pdf.logicalstructure.HeaderElement:
        '''Creates :class:`aspose.pdf.logicalstructure.HeaderElement` with level.
        
        :param level: The level of Header. Must be 1, 2, 3, 4, 5 or 6.
        :returns: Created structure element.'''
        ...
    
    def set_language(self, lang: str) -> None:
        '''Sets natural language for pdf document.
        
        A language identifier that shall specify the natural language for all text in the document except where overridden by language specifications for structure elements or marked content.
        
        :param lang: A language identifier shall either be the empty text string, to indicate that the language is unknown, or a Language-Tag as defined in RFC 3066, Tags for the Identification of Languages.'''
        ...
    
    def set_title(self, title: str) -> None:
        '''Sets title for PDF document.
        
        :param title: The title of PDF document.'''
        ...
    
    def create_part_element(self) -> aspose.pdf.logicalstructure.PartElement:
        '''Creates :class:`aspose.pdf.logicalstructure.PartElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_art_element(self) -> aspose.pdf.logicalstructure.ArtElement:
        '''Creates :class:`aspose.pdf.logicalstructure.ArtElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_sect_element(self) -> aspose.pdf.logicalstructure.SectElement:
        '''Creates :class:`aspose.pdf.logicalstructure.SectElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_div_element(self) -> aspose.pdf.logicalstructure.DivElement:
        '''Creates :class:`aspose.pdf.logicalstructure.DivElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_block_quote_element(self) -> aspose.pdf.logicalstructure.BlockQuoteElement:
        '''Creates :class:`aspose.pdf.logicalstructure.BlockQuoteElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_caption_element(self) -> aspose.pdf.logicalstructure.CaptionElement:
        '''Creates :class:`aspose.pdf.logicalstructure.CaptionElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_toc_element(self) -> aspose.pdf.logicalstructure.TOCElement:
        '''Creates :class:`aspose.pdf.logicalstructure.TOCElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_toci_element(self) -> aspose.pdf.logicalstructure.TOCIElement:
        '''Creates :class:`aspose.pdf.logicalstructure.TOCIElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_index_element(self) -> aspose.pdf.logicalstructure.IndexElement:
        '''Creates :class:`aspose.pdf.logicalstructure.IndexElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_non_struct_element(self) -> aspose.pdf.logicalstructure.NonStructElement:
        '''Creates :class:`aspose.pdf.logicalstructure.NonStructElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_private_element(self) -> aspose.pdf.logicalstructure.PrivateElement:
        '''Creates :class:`aspose.pdf.logicalstructure.PrivateElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_paragraph_element(self) -> aspose.pdf.logicalstructure.ParagraphElement:
        '''Creates :class:`aspose.pdf.logicalstructure.ParagraphElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_list_element(self) -> aspose.pdf.logicalstructure.ListElement:
        '''Creates :class:`aspose.pdf.logicalstructure.ListElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_list_li_element(self) -> aspose.pdf.logicalstructure.ListLIElement:
        '''Creates :class:`aspose.pdf.logicalstructure.ListLIElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_list_lbl_element(self) -> aspose.pdf.logicalstructure.ListLblElement:
        '''Creates :class:`aspose.pdf.logicalstructure.ListLblElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_list_l_body_element(self) -> aspose.pdf.logicalstructure.ListLBodyElement:
        '''Creates :class:`aspose.pdf.logicalstructure.ListLBodyElement`.
        
        :returns: Created structure element.'''
        ...

    def create_table_element(self) -> aspose.pdf.logicalstructure.TableElement:
        '''Creates :class:`aspose.pdf.logicalstructure.TableElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_table_t_head_element(self) -> aspose.pdf.logicalstructure.TableTHeadElement:
        '''Creates :class:`aspose.pdf.logicalstructure.TableTHeadElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_table_t_body_element(self) -> aspose.pdf.logicalstructure.TableTBodyElement:
        '''Creates :class:`aspose.pdf.logicalstructure.TableTHeadElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_table_t_foot_element(self) -> aspose.pdf.logicalstructure.TableTFootElement:
        '''Creates :class:`aspose.pdf.logicalstructure.TableTFootElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_table_tr_element(self) -> aspose.pdf.logicalstructure.TableTRElement:
        '''Creates :class:`aspose.pdf.logicalstructure.TableTRElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_table_th_element(self) -> aspose.pdf.logicalstructure.TableTHElement:
        '''Creates :class:`aspose.pdf.logicalstructure.TableTHElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_table_td_element(self) -> aspose.pdf.logicalstructure.TableTDElement:
        '''Creates :class:`aspose.pdf.logicalstructure.TableTDElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_span_element(self) -> aspose.pdf.logicalstructure.SpanElement:
        '''Creates :class:`aspose.pdf.logicalstructure.SpanElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_quote_element(self) -> aspose.pdf.logicalstructure.QuoteElement:
        '''Creates :class:`aspose.pdf.logicalstructure.QuoteElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_note_element(self) -> aspose.pdf.logicalstructure.NoteElement:
        '''Creates :class:`aspose.pdf.logicalstructure.NoteElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_reference_element(self) -> aspose.pdf.logicalstructure.ReferenceElement:
        '''Creates :class:`aspose.pdf.logicalstructure.ReferenceElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_bib_entry_element(self) -> aspose.pdf.logicalstructure.BibEntryElement:
        '''Creates :class:`aspose.pdf.logicalstructure.BibEntryElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_code_element(self) -> aspose.pdf.logicalstructure.CodeElement:
        '''Creates :class:`aspose.pdf.logicalstructure.CodeElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_link_element(self) -> aspose.pdf.logicalstructure.LinkElement:
        '''Creates :class:`aspose.pdf.logicalstructure.LinkElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_annot_element(self) -> aspose.pdf.logicalstructure.AnnotElement:
        '''Creates :class:`aspose.pdf.logicalstructure.AnnotElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_ruby_element(self) -> aspose.pdf.logicalstructure.RubyElement:
        '''Creates :class:`aspose.pdf.logicalstructure.RubyElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_warichu_element(self) -> aspose.pdf.logicalstructure.WarichuElement:
        '''Creates :class:`aspose.pdf.logicalstructure.WarichuElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_figure_element(self) -> aspose.pdf.logicalstructure.FigureElement:
        '''Creates :class:`aspose.pdf.logicalstructure.FigureElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_formula_element(self) -> aspose.pdf.logicalstructure.FormulaElement:
        '''Creates :class:`aspose.pdf.logicalstructure.FormulaElement`.
        
        :returns: Created structure element.'''
        ...
    
    def create_form_element(self) -> aspose.pdf.logicalstructure.FormElement:
        '''Creates :class:`aspose.pdf.logicalstructure.FormElement`.
        
        :returns: Created structure element.'''
        ...
    
    def pre_save(self) -> None:
        '''Prepares the tagged content of the document for saving.
        This method performs necessary pre-save operations, ensuring that the
        structure tree and other tagged content elements are properly configured
        before the document is saved.'''
        ...
    
    def save(self) -> None:
        '''Saves the current state of the tagged content to the associated PDF document.
        
        This method ensures that all tagged content elements are properly updated and saved within the PDF document.
        It performs necessary operations such as updating MCID for MCR elements, setting BDC operators, and ensuring
        compliance with PDF/UA standards.'''
        ...

    @property
    def structure_text_state(self) -> aspose.pdf.logicalstructure.StructureTextState:
        '''Get :class:`aspose.pdf.logicalstructure.StructureTextState` settings for whole document.'''
        ...
    
    @property
    def struct_tree_root_element(self) -> aspose.pdf.logicalstructure.StructTreeRootElement:
        '''Gets :class:`aspose.pdf.logicalstructure.StructTreeRootElement` of PDF document.'''
        ...
    
    @property
    def root_element(self) -> aspose.pdf.logicalstructure.StructureElement:
        '''Gets root :class:`aspose.pdf.logicalstructure.StructureElement` of logical structure of PDF document.'''
        ...
    
    ...

class PositionSettings:
    '''Position settings.'''
    
    def __init__(self):
        ...
    
    @property
    def horizontal_alignment(self) -> aspose.pdf.HorizontalAlignment:
        '''Gets or sets a horizontal alignment of paragraph.'''
        ...
    
    @horizontal_alignment.setter
    def horizontal_alignment(self, value: aspose.pdf.HorizontalAlignment):
        ...
    
    @property
    def margin(self) -> aspose.pdf.MarginInfo:
        '''Gets or sets a outer margin for paragraph.'''
        ...
    
    @margin.setter
    def margin(self, value: aspose.pdf.MarginInfo):
        ...
    
    @property
    def vertical_alignment(self) -> aspose.pdf.VerticalAlignment:
        '''Gets or sets a vertical alignment of paragraph.'''
        ...
    
    @vertical_alignment.setter
    def vertical_alignment(self, value: aspose.pdf.VerticalAlignment):
        ...
    
    @property
    def is_first_paragraph_in_column(self) -> bool:
        '''Gets or sets a bool value that indicates whether this paragraph will be at next column.
        Default is false.'''
        ...
    
    @is_first_paragraph_in_column.setter
    def is_first_paragraph_in_column(self, value: bool):
        ...
    
    @property
    def is_kept_with_next(self) -> bool:
        '''Gets or sets a bool value that indicates whether current paragraph remains in the same page along with next paragraph.
        Default is false.'''
        ...
    
    @is_kept_with_next.setter
    def is_kept_with_next(self, value: bool):
        ...
    
    @property
    def is_in_new_page(self) -> bool:
        '''Gets or sets a bool value that force this paragraph generates at new page.
        Default is false.'''
        ...
    
    @is_in_new_page.setter
    def is_in_new_page(self, value: bool):
        ...
    
    @property
    def is_in_line_paragraph(self) -> bool:
        '''Gets or sets a paragraph is inline.
        Default is false.'''
        ...
    
    @is_in_line_paragraph.setter
    def is_in_line_paragraph(self, value: bool):
        ...
    
    ...

class TaggedException(aspose.pdf.PdfException):
    '''Represents exception for TaggedPDF content of document.'''
    
    def __init__(self):
        '''Initializes a new instance of the :class:`TaggedException` class.'''
        ...
    
    ...


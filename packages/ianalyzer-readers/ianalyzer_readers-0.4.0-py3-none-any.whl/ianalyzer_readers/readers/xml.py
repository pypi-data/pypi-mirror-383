'''
This module defines the XML Reader.

Extraction is based on BeautifulSoup.
'''

import bs4
import logging
from typing import Dict, Iterable, List, Optional
from requests import Response

from .. import extract
from .core import Reader, Document, Field
from ..xml_tag import CurrentTag, resolve_tag_specification, TagSpecification


logger = logging.getLogger()

class XMLReader(Reader):
    '''
    A base class for Readers that extract data from XML files.

    The built-in functionality of the XML reader is quite versatile, and can be further
    expanded by adding custom Tag classes or extraction functions that interact directly with
    BeautifulSoup nodes.

    The Reader is suitable for datasets where each file should be extracted as a single
    document, or ones where each file contains multiple documents.

    In addition to generic extractor classes, this reader supports the `XML` extractor.

    Attributes:
        tag_toplevel: the top-level tag to search from in source documents.
        tag_entry: the tag that corresponds to a single document entry in source
            documents.
        external_file_tag_toplevel: the top-level tag to search from in external
            documents (if that functionality is used)

    '''

    tag_toplevel: TagSpecification = CurrentTag()
    '''
    The top-level tag in the source documents.

    Can be:

    - An XMLTag
    - A callable that takes the metadata of the document as input and returns an
        XMLTag.
    '''

    tag_entry: TagSpecification = CurrentTag()
    '''
    The tag that corresponds to a single document entry.

    Can be:

    - An XMLTag
    - A callable that takes the metadata of the document as input and returns an
        XMLTag
    '''

    external_file_tag_toplevel: TagSpecification = CurrentTag()
    '''
    The toplevel tag in external files (if you are using that functionality).

    Can be:

    - An XMLTag
    - A callable that takes the metadata of the document as input and returns an
        XMLTag. The metadata dictionary includes the values of "regular" fields for
        the document.
    '''

    def validate(self):
        # Make sure that extractors are sensible
        self._reject_extractors(extract.CSV)

    def iterate_data(self, data: bs4.BeautifulSoup, metadata: Dict) -> Iterable[Document]:
        external_soup = self._external_soup(metadata)

        # iterate through entries
        top_tag = resolve_tag_specification(self.__class__.tag_toplevel, metadata)
        bowl = top_tag.find_next_in_soup(data)

        if bowl:
            entry_tag = resolve_tag_specification(self.__class__.tag_entry, metadata)
            spoonfuls = entry_tag.find_in_soup(bowl)
            for spoon in spoonfuls:
                yield {
                    'soup_top': bowl,
                    'soup_entry': spoon,
                    'external_soup': external_soup,
                }
        else:
            logger.warning('Top-level tag not found')

    def extract_document(self, **document_data) -> Document:
        external_fields = self._external_fields()
        # fields should have unique names, but may not have stable instantiations
        # if FieldDefinitions are created on the fly, for example with class methods or @propertys
        external_fields_names = set(field.name for field in external_fields)
        regular_fields = [
            field for field in self.fields
            if field.name not in external_fields_names
        ]

        field_dict = {
            field.name: field.extractor.apply(**document_data)
            for field in regular_fields if not field.skip
        }

        external_soup = document_data.get('external_soup', None)
        metadata = document_data.get('metadata')

        if external_fields and external_soup:
            external_dict = self._external_source2dict(
                external_soup, external_fields, metadata | field_dict)
        else:
            external_dict = {
                field.name: None for field in external_fields if not field.skip
            }

        # yield the union of external fields and document fields
        return field_dict | external_dict

    def _external_fields(self) -> List[Field]:
        '''
        Subset of the reader's fields that rely on an external XML file.
        '''
        return [field for field in self.fields if
            isinstance(field.extractor, extract.XML) and field.extractor.external_file
        ]

    def _external_soup(self, metadata: Dict) -> Optional[bs4.BeautifulSoup]:
        '''
        Returns parsed tree for the external XML file, if applicable
        '''
        if any(self._external_fields()):
            if metadata and 'external_file' in metadata:
                return self.data_from_file(metadata['external_file'])
            else:
                logger.warning(
                    'Some fields have external_file property, but no external file is '
                    'provided in the source metadata'
                )

    def _external_source2dict(self, soup, external_fields: List[Field], metadata: Dict):
        '''
        given an external xml file with metadata,
        return a dictionary with tags which were found in that metadata
        wrt to the current source.
        '''
        tag = resolve_tag_specification(self.__class__.external_file_tag_toplevel, metadata)
        bowl = tag.find_next_in_soup(soup)

        if not bowl:
            logger.warning(
                'Top-level tag not found in `{}`'.format(metadata['external_file']))
            return {field.name: None for field in external_fields if not field.skip}

        return {
            field.name: field.extractor.apply(
                soup_top=bowl, soup_entry=bowl, metadata=metadata
            )
            for field in external_fields if not field.skip
        }

    def data_from_file(self, filename: str) -> bs4.BeautifulSoup:
        '''
        Returns beatifulsoup soup object for a given xml file
        '''
        # Loading XML
        logger.info('Reading XML file {} ...'.format(filename))
        with open(filename, 'rb') as f:
            data = f.read()
        logger.info('Loaded {} into memory...'.format(filename))
        return self.data_from_bytes(data)

    def data_from_bytes(self, data: bytes) -> bs4.BeautifulSoup:
        '''
        Parses content of a xml file
        '''
        return bs4.BeautifulSoup(data, 'lxml-xml')

    def data_from_response(self, data: Response) -> bs4.BeautifulSoup:
        return bs4.BeautifulSoup(data.content, 'lxml-xml')

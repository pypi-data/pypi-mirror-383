from tulit.parsers.xml.xml import XMLParser
import json
import argparse

class AkomaNtosoParser(XMLParser):
    """
    A parser for processing and extracting content from AkomaNtoso files.

    The parser handles XML documents following the Akoma Ntoso 3.0 schema for legal documents.
    It inherits from the XMLParser class and provides methods to extract various components
    like preface, preamble, chapters, articles, and conclusions.
    
    Attributes
    ----------
    namespaces : dict
        Dictionary mapping namespace prefixes to their URIs.
    """
    def __init__(self):
        """
        Initializes the parser.
        """
        super().__init__()
                
        # Define the namespace mapping
        self.namespaces = {
            'akn': 'http://docs.oasis-open.org/legaldocml/ns/akn/3.0',
            'an': 'http://docs.oasis-open.org/legaldocml/ns/akn/3.0',
            'fmx': 'http://formex.publications.europa.eu/schema/formex-05.56-20160701.xd'

        }
    
    def get_preface(self):
        """	
        Extracts preface information from the document. It is assumed that the preface
        is contained within the 'preface' element in the XML file.
        """
        return super().get_preface(preface_xpath='.//akn:preface', paragraph_xpath='.//akn:p')
    
    def get_preamble(self):
        """
        Extracts preamble information from the document. It is assumed that the preamble
        is contained within the 'preamble' element in the XML file.
        """
        return super().get_preamble(preamble_xpath='.//akn:preamble', notes_xpath='.//akn:authorialNote')
    
    def get_formula(self):
        """
        Extracts formula text from the preamble. The formula is assumed to be contained
        within the 'formula' element in the XML file. The formula text is extracted from
        all paragraphs within the formula element.

        Returns
        -------
        str or None
            Concatenated text from all paragraphs within the formula element.
            Returns None if no formula is found.
        """
        return super().get_formula(formula_xpath='.//akn:formula', paragraph_xpath='akn:p')
    
    def get_citations(self) -> list:
        """
        Extracts citations from the preamble. The citations are assumed to be contained
        within the 'citations' element in the XML file. Each citation is extracted from
        the 'citation' element within the citations element. The citation text is extracted
        from all paragraphs within the citation element. 

        """
        

        return super().get_citations(
            citations_xpath='.//akn:citations',
            citation_xpath='.//akn:citation',
            extract_eId=self.extract_eId
        )
    
    def get_recitals(self):
        """
        Extracts recitals from the preamble. The recitals are assumed to be contained
        within the 'recitals' element in the XML file. Each recital is extracted from
        the 'recital' element within the recitals element. The recital text is extracted
        from all paragraphs within the recital element.

        Returns
        -------
        list or None
            List of dictionaries containing recital text and eId for each
            recital. Returns None if no recitals are found.
        """
        
        def extract_intro(recitals_section):
            recitals_intro = recitals_section.find('.//akn:intro', namespaces=self.namespaces)
            intro_eId = self.extract_eId(recitals_intro, 'eId')
            intro_text = ''.join(p.text.strip() for p in recitals_intro.findall('.//akn:p', namespaces=self.namespaces) if p.text)
            return intro_eId, intro_text
        
        #def extract_eId(recital):
        #    return str(recital.get('eId'))
        
        return super().get_recitals(
            recitals_xpath='.//akn:recitals', 
            recital_xpath='.//akn:recital',
            text_xpath='.//akn:p',
            extract_intro=extract_intro,
            extract_eId=self.extract_eId,
            
        )
    
    def get_preamble_final(self):
        """
        Extracts the final preamble text from the document. The final preamble is assumed
        to be contained within the 'preamble.final' element in the XML file. 

        Returns
        -------
        str or None
            Concatenated text from the final preamble element.
            Returns None if no final preamble is found.
        """
        return super().get_preamble_final(preamble_final_xpath='.//akn:block[@name="preamble.final"]')
    
    
    def get_body(self):
        """
        Extracts the body section from the document. The body is assumed to be contained
        within the 'body' element in the XML file.
        """
        return super().get_body('.//akn:body')
    
    def extract_eId(self, element, index=None):
        return element.get('eId')
        
    def get_chapters(self) -> None:
        """
        Extracts chapter information from the document. The chapters are assumed to be
        contained within the 'chapter' element in the XML file. Each chapter is extracted
        from the 'chapter' element. The chapter number and heading are extracted from the
        'num' and 'heading' elements within the chapter element. The chapter identifier
        is extracted from the 'eId' attribute of the chapter element.

        Returns
        -------
        list
            List of dictionaries containing chapter data with keys:
            - 'eId': Chapter identifier
            - 'chapter_num': Chapter number
            - 'chapter_heading': Chapter heading text
        """
        

        return super().get_chapters(
            chapter_xpath='.//akn:chapter',
            num_xpath='.//akn:num',
            heading_xpath='.//akn:heading',
            extract_eId=self.extract_eId
        )

    
    def get_articles(self) -> None:
        """
        Extracts article information from the document. The articles are assumed to be
        contained within the 'article' element in the XML file. Each article is extracted
        from the 'article' element. The article number and title are extracted from the
        'num' and 'heading' elements within the article element. The article identifier
        is extracted from the 'eId' attribute of the article element. The article is further
        divided into child elements.
    
        Returns
        -------
        list
            List of dictionaries containing article data with keys:
            - 'eId': Article identifier
            - 'article_num': Article number
            - 'article_title': Article title
            - 'children': List of dictionaries with eId and text content
        """        
        # Removing all authorialNote nodes
        self.body = self.remove_node(self.body, './/akn:authorialNote')

        # Find all <article> elements in the XML
        for article in self.body.findall('.//akn:article', namespaces=self.namespaces):
            eId = self.extract_eId(article, 'eId')
            
            # Find the main <num> element representing the article number
            article_num = article.find('akn:num', namespaces=self.namespaces)
            article_num_text = ''.join(article_num.itertext()).strip() if article_num is not None else None

            # Find a secondary <num> or <heading> to represent the article title or subtitle, if present
            article_title_element = article.find('akn:heading', namespaces=self.namespaces)
            if article_title_element is None:
                # If <heading> is not found, use the second <num> as the title if it exists
                article_title_element = article.findall('akn:num', namespaces=self.namespaces)[1] if len(article.findall('akn:num', namespaces=self.namespaces)) > 1 else None
            # Get the title text 
            article_title_text = ''.join(article_title_element.itertext()).strip() if article_title_element is not None else None

            children = self.get_text_by_eId(article)
        
            # Append the article data to the articles list
            self.articles.append({
                'eId': eId,
                'num': article_num_text,
                'heading': article_title_text,
                'children': children
            })

    
    def get_text_by_eId(self, node):
        """
        Groups paragraph text by their nearest parent element with an eId attribute.

        Parameters
        ----------
        node : lxml.etree._Element
            XML node to process for text extraction.

        Returns
        -------
        list
            List of dictionaries containing:
            - 'eId': Identifier of the nearest parent with an eId
            - 'text': Concatenated text content
        """
        elements = []
        # Find all <p> elements
        for p in node.findall('.//akn:p', namespaces=self.namespaces):
            # Traverse up to find the nearest parent with an eId
            current_element = p
            eId = None
            while current_element is not None:
                eId = self.extract_eId(current_element, 'eId')                
                if eId:
                    break
                current_element = current_element.getparent()  # Traverse up

            # If an eId is found, add <p> text to the eId_text_map
            if eId:
                # Capture the full text within the <p> tag, including nested elements
                p_text = ''.join(p.itertext()).strip()
                element = {
                    'eId': eId,
                    'text': p_text
                }
                elements.append(element)
        return elements
    
    def get_conclusions(self):
        """
        Extracts conclusions information from the document. The conclusions are assumed to be
        contained within the 'conclusions' element in the XML file. The conclusions section
        may contain multiple <p> elements, each containing one or more <signature> elements.
        The signature elements contain the signature text and metadata. The date is extracted
        from the first <signature> element.

        Returns
        -------
        None
        """
        conclusions_section = self.root.find('.//akn:conclusions', namespaces=self.namespaces)
        if conclusions_section is None:
            return None

        # Find the container with signatures
        container = conclusions_section.find('.//akn:container[@name="signature"]', namespaces=self.namespaces)
        if container is None:
            return None

        # Extract date from the first <signature>
        date_element = container.find('.//akn:date', namespaces=self.namespaces)
        signature_date = date_element.text if date_element is not None else None

        # Extract all signatures
        signatures = []
        for p in container.findall('akn:p', namespaces=self.namespaces):
            # For each <p>, find all <signature> tags
            paragraph_signatures = []
            for signature in p.findall('akn:signature', namespaces=self.namespaces):
                # Collect text within the <signature>, including nested elements
                signature_text = ''.join(signature.itertext()).strip()
                paragraph_signatures.append(signature_text)

            # Add the paragraph's signatures as a group
            if paragraph_signatures:
                signatures.append(paragraph_signatures)

        # Store parsed conclusions data
        self.conclusions = {
            'date': signature_date,
            'signatures': signatures
        }
    
    def parse(self, file: str) -> None:
        """
        Parses an Akoma Ntoso 3.0 document to extract its components, which are inherited from the XMLParser class
        """
        return super().parse(file, schema = 'akomantoso30.xsd', format = 'Akoma Ntoso')

class AKN4EUParser(AkomaNtosoParser):
    """
    A parser for processing and extracting content from AAKN4EU files.
    
    This class is a subclass of the AkomaNtosoParser class and is specifically designed to handle
    AKN4EU documents. It inherits all methods and attributes from the parent class.
    
    Attributes
    ----------
    namespaces : dict
        Dictionary mapping namespace prefixes to their URIs.
    """
    def __init__(self):
        super().__init__()

    def extract_eId(self, element, index=None):
        return element.get('{http://www.w3.org/XML/1998/namespace}id')
    
    def get_text_by_eId(self, node):
        """
        Groups paragraph text by their nearest parent element with an eId attribute.

        Parameters
        ----------
        node : lxml.etree._Element
            XML node to process for text extraction.

        Returns
        -------
        list
            List of dictionaries containing:
            - 'eId': Identifier of the nearest parent with an eId
            - 'text': Concatenated text content
        """
        elements = []
        # Find all <paragraph> elements
        for p in node.findall('.//akn:paragraph', namespaces=self.namespaces):
            # Traverse up to find the nearest parent with an xml:id                        
            eId = self.extract_eId(p, 'xml:id')                                
            import re
            p_text = re.sub(r'\s+', ' ', ''.join(p.itertext()).replace('\n', '').replace('\r', '').strip())
            element = {
                    'eId': eId,
                    'text': p_text
            }
            elements.append(element)
        return elements

def main():
    parser = argparse.ArgumentParser(description='Parse an Akoma Ntoso XML document and output the results to a JSON file.')
    parser.add_argument('--input', type=str, default='tests/data/akn/eu/32014L0092.akn', help='Path to the Akoma Ntoso XML file to parse.')
    parser.add_argument('--output', type=str, default='tests/data/json/akn.json', help='Path to the output JSON file.')
    parser.add_argument('--format', type=str, default='akn', help='Dialect of Akoma Ntoso to parse.')
    args = parser.parse_args()
    if args.format == 'akn':
        akoma_parser = AkomaNtosoParser()
    elif args.format == 'akn4eu':
        akoma_parser = AKN4EUParser()
    akoma_parser.parse(args.input)
    with open(args.output, 'w', encoding='utf-8') as f:
        # Get the parser's attributes as a dictionary
        parser_dict = akoma_parser.__dict__
        # Filter out non-serializable attributes
        serializable_dict = {k: v for k, v in parser_dict.items() if isinstance(v, (str, int, float, bool, list, dict, type(None)))}
        # Write to a JSON file
        json.dump(serializable_dict, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()


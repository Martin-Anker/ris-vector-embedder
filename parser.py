from typing import List
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re

from http_requests import fetch_ris_html

def parse_ris_article_page(html_content):
    """
    Scrapes Austrian legal documents from RIS (Rechtsinformationssystem).
    
    Args:
        html_content (str): HTML content of the document
        
    Returns:
        dict: Extracted fields
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    result = {}
    absatz_list = []
    
    # Extract Kurztitel
    kurztitel_div = soup.find('h3', string='Kurztitel')
    if kurztitel_div and kurztitel_div.parent:
        result['Kurztitel'] = kurztitel_div.parent.get_text(strip=True).replace('Kurztitel', '').strip()
    
    # Extract Typ
    typ_div = soup.find('h3', string='Typ')
    if typ_div and typ_div.parent:
        result['Typ'] = typ_div.parent.get_text(strip=True).replace('Typ', '').strip()

    # Extract §/Artikel/Anlage
    artikel_div = soup.find('h3', string='§/Artikel/Anlage')
    if artikel_div and artikel_div.parent:
        result['Paragraph_Artikel_Anlage'] = artikel_div.parent.get_text(strip=True).replace('§/Artikel/Anlage', '').strip()    
    
    # Extract Inkrafttretensdatum
    inkraft_div = soup.find('h3', string='Inkrafttretensdatum')
    if inkraft_div and inkraft_div.parent:
        result['Inkrafttretensdatum'] = inkraft_div.parent.get_text(strip=True).replace('Inkrafttretensdatum', '').strip()
    
    # Extract Index
    index_div = soup.find('h3', string='Index')
    if index_div and index_div.parent:
        result['Index'] = index_div.parent.get_text(strip=True).replace('Index', '').strip()
    
    # Extract Text and Absätze
    text_container = soup.find('div', id=re.compile(r'.*TextContainer.*'))
    if text_container:
        # Check if there are numbered Absätze (paragraphs)
        absatz_items = text_container.find_all('li')
        
        if absatz_items:
            # Case 1: Multiple Absätze with numbering
            for idx, li in enumerate(absatz_items):
                # Find the content div
                content_div = li.find('div', class_='content')
                if content_div:
                    # Get text, preserving structure
                    text = content_div.get_text(separator=' ', strip=True)
                    
                    # Remove paragraph symbol from first Absatz only
                    if idx == 0:
                        # Remove paragraph symbols like "§ 13a." or "§ 3."
                        text = re.sub(r'^§\s*\d+[a-z]*\.\s*', '', text)
                        text = re.sub(r'^Paragraph\s+\d+[a-z]*,?\s*', '', text, flags=re.IGNORECASE)
                    
                    # Remove Absatz numbering like "(1)" or "Absatz eins"
                    text = re.sub(r'^\(\d+\)\s*', '', text)
                    text = re.sub(r'^Absatz\s+\w+\s*', '', text, flags=re.IGNORECASE)
                    
                    absatz_list.append(text.strip())
            
            # Store full text
            text_content = text_container.get_text(separator='\n', strip=True)
            text_content = text_content.replace('Text', '', 1).strip()
        else:
            # Case 2: Single paragraph without numbering
            # Find the main paragraph
            main_para = text_container.find('p', class_='Abs')
            if main_para:
                text = main_para.get_text(separator=' ', strip=True)
                
                # Remove paragraph symbol
                text = re.sub(r'^§\s*\d+[a-z]*\.\s*', '', text)
                text = re.sub(r'^Paragraph\s+\d+[a-z]*,?\s*', '', text, flags=re.IGNORECASE)
                
                absatz_list.append(text.strip())
            else:
                # Fallback: get all text
                text_content = text_container.get_text(separator='\n', strip=True)
                text_content = text_content.replace('Text', '', 1).strip()
                if text_content:
                    absatz_list.append(text_content)
    else:
        # If no Text field, try Titel field
        titel_div = soup.find('h3', string='Titel')
        if titel_div and titel_div.parent:
            titel_content = titel_div.parent.get_text(separator=' ', strip=True)
            titel_content = titel_content.replace('Titel', '', 1).strip()
            absatz_list.append(titel_content)
    
    # Extract Schlagworte
    schlagworte_div = soup.find('h3', string='Schlagworte')
    if schlagworte_div and schlagworte_div.parent:
        result['Schlagworte'] = schlagworte_div.parent.get_text(strip=True).replace('Schlagworte', '').strip()
    
    # Extract Gesetzesnummer
    gesetz_div = soup.find('h3', string='Gesetzesnummer')
    if gesetz_div and gesetz_div.parent:
        result['Gesetzesnummer'] = gesetz_div.parent.get_text(strip=True).replace('Gesetzesnummer', '').strip()
    
    # Extract Dokumentnummer
    dokument_div = soup.find('h3', string='Dokumentnummer')
    if dokument_div and dokument_div.parent:
        # Get text and extract just the document number (not "Alte Dokumentnummer")
        parent_text = dokument_div.parent.get_text(strip=True)
        # Extract document number before "Alte Dokumentnummer" if present
        if 'Alte Dokumentnummer' in parent_text:
            result['Dokumentnummer'] = parent_text.replace('Dokumentnummer', '').split('Alte Dokumentnummer')[0].strip()
        else:
            result['Dokumentnummer'] = parent_text.replace('Dokumentnummer', '').strip()
    
    return result, absatz_list

def loop_through_ris_articles(list_url: str, gesetzesNummer: str | None = None) -> List[str]:
    """
    Fetch and parse multiple RIS articles from a listing page.
    
    Args:
        list_url (str): URL of the RIS listing page
        
    Returns:
        List[str]: List of document URLs
    """
    html = fetch_ris_html(list_url)
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all table rows with document data
    rows = soup.find_all('tr', class_='bocListDataRow')
    
    document_urls = []

    base_url = "https://www.ris.bka.gv.at"
    
    for row in rows:
        # Extract the document link from the §/Art./Anl. column
        link_cell = row.find_all('td', class_='bocListDataCell')
        if link_cell:
            link = link_cell[2].find('a')
            if link and link.get('href'):
                # Construct full URL
                doc_url = urljoin(base_url, link['href'])
                #print(f"Found document URL: {doc_url}")
                document_urls.append(doc_url)
    
    return document_urls
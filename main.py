import os
import sys
from typing import Optional

from bs4 import BeautifulSoup

from http_requests import fetch_ris_html
from parser import loop_through_ris_articles, parse_ris_article_page

def parse_paragraphs(html: str) -> Optional[str]:
	"""Optional: parse the page title from the HTML for quick verification."""
	soup = BeautifulSoup(html, "html.parser")

	paragraphs = []

	doc_content = soup.find_all(class_="documentContent")
	for content in doc_content:
		content_blocks = content.find(class_="contentBlock")
		# Multiple absätze in paragraph
		if content_blocks:
			current_paragraph_number = soup.find(class_="GldSymbolFloatLeft")
			if current_paragraph_number:
				current_paragraph_number = current_paragraph_number.get_text(strip=True)
			else:
				current_paragraph_number = ""
			absatz_element = content_blocks.find(class_="wai-absatz-list")
			#loop through list
			if not absatz_element:
				continue
			absatz_items = absatz_element.find_all("li")
			for item in absatz_items:
				absatz_text = item.get_text(strip=True)
				paragraphs.append(f"{current_paragraph_number} {absatz_text}")
				print(f"{current_paragraph_number} {absatz_text}")
				print("------------------------------")
		else:
			#get text value of paragraph
			paragraphs.append(content.get_text(strip=True))
			print(content.get_text(strip=True))
			print("------------------------------")
	return "\n".join(paragraphs)


def main() -> None:
	# Example RIS URL
	ris_url = "https://www.ris.bka.gv.at/Ergebnis.wxe?Abfrage=Bundesnormen&Kundmachungsorgan=&Index=&Titel=&Gesetzesnummer=&VonArtikel=&BisArtikel=&VonParagraf=&BisParagraf=&VonAnlage=&BisAnlage=&Typ=&Kundmachungsnummer=&Unterzeichnungsdatum=&FassungVom=16.12.2025&VonInkrafttretedatum=&BisInkrafttretedatum=&VonAusserkrafttretedatum=&BisAusserkrafttretedatum=&NormabschnittnummerKombination=Und&ImRisSeitVonDatum=&ImRisSeitBisDatum=&ImRisSeit=Undefined&ResultPageSize=100&Suchworte=&Position=1&SkipToDocumentPage=true"
	article_urls = loop_through_ris_articles(ris_url)

	for url in article_urls:
		html = fetch_ris_html(url)
		article_data, absatz_list = parse_ris_article_page(html)

		print("Article Data:")
		for key, value in article_data.items():
			print(f"{key}: {value}\n")
		print("Paragraphs:")
		for i, paragraph in enumerate(absatz_list, start=1):
			print(f"Absatz {i}: {paragraph}\n")

		print("=====================================\n")
		

		
	#print(paragraph_list)


if __name__ == "__main__":
	main()
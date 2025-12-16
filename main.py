import os
import sys
from typing import Optional

import requests
from bs4 import BeautifulSoup

RIS_URL = (
	"https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20002128"
)

def fetch_ris_html(url: str = RIS_URL, timeout: int = 20) -> str:
	"""Fetch raw HTML from the given RIS URL.

	Raises requests.HTTPError on non-200 responses.
	"""
	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
		" AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
	}
	resp = requests.get(url, headers=headers, timeout=timeout)
	resp.raise_for_status()
	# Ensure we treat content as text with apparent encoding
	resp.encoding = resp.apparent_encoding or resp.encoding
	return resp.text


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
				print(f"Added paragraph: {current_paragraph_number} {absatz_text}")
				print("------------------------------")
		else:
			#get text value of paragraph
			paragraphs.append(content.get_text(strip=True))
	return "\n".join(paragraphs)


def main() -> None:
	html = fetch_ris_html()
	paragraph_list = parse_paragraphs(html)
	#print(paragraph_list)


if __name__ == "__main__":
	main()
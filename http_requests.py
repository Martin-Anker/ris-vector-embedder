import requests

def fetch_ris_html(url: str, timeout: int = 20) -> str:
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
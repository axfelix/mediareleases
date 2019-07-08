from bs4 import BeautifulSoup
import re
import sys
import os
from lxml.html import fromstring

with open(sys.argv[1], "r", encoding='ISO-8859-1') as release:
	html_doc = release.read()
root = fromstring(html_doc)

if '<div class="p1">' in html_doc:
	junked = html_doc[html_doc.find('<div class="p1">'):]
else:
	junked = html_doc[html_doc.find('<!-- PAGE CONTENT -->'):]
soup = BeautifulSoup(junked, 'html.parser')
text_only = soup.get_text()

if '-30-' in text_only:
	chop_dash = text_only[:text_only.find('-30-')]
elif '\x9630\x96' in text_only:
	chop_dash = text_only[:text_only.find('\x9630\x96')]
elif '\x9730\x97' in text_only:
	chop_dash = text_only[:text_only.find('\x9730\x97')]
elif '- 30 -' in text_only:
	chop_dash = text_only[:text_only.find('- 30 -')]
elif '- 30-' in text_only:
	chop_dash = text_only[:text_only.find('- 30-')]
elif '-30 -' in text_only:
	chop_dash = text_only[:text_only.find('-30 -')]
elif '-30-' in text_only:
	chop_dash = text_only[:text_only.find('-30-')]
else:
	chop_dash = text_only
if 'Printer-Friendly Version' in chop_dash:
	printer_unfriendly = chop_dash[:chop_dash.find('Printer-Friendly Version')]
elif 'For the Media' in chop_dash:
	printer_unfriendly = chop_dash[:chop_dash.find('For the Media')]
else:
	printer_unfriendly = chop_dash

whitespaced = re.sub(r"([^0-9])\.([^\sa-z\"\x94,\)])(?!\.)", r"\1.\n\n\2", printer_unfriendly)
phoned = re.sub(r"([0-9]{4})([A-Z])", r"\1\n\2", whitespaced)
chopped = re.sub(r"@([a-z]+)\.(ca|org|com)(?!\.)", r"@\1.\2\n", phoned)
chopped = chopped.replace("\u2018", "'")
chopped = chopped.replace("\u2019", "'")
chopped = chopped.replace("\u201c", "'")
chopped = chopped.replace("\u201d", "'")
chopped = chopped.replace("\x92", "'")
chopped = chopped.replace("\x93", '"')
chopped = chopped.replace("\x94", '"')
chopped = chopped.replace("\u2013", "-")
chopped = chopped.replace("\x96", "-")
chopped = chopped.replace("\u2014", "-")
chopped = chopped.replace("\u2022", "-")
chopped = chopped.replace("\x97", "-")
chopped = chopped.replace("\u2026", "...")
chopped = chopped.replace("\u2122", "(TM)")
commaed = re.sub(r"\n'\n", "'\n", chopped)
released = re.sub(r"\n(Yes|No)\n", "\n\n", commaed)
redacted = re.sub(r"\(?\d{3}\)?(.|-)?\d{3}(.|-)?\d{4}", "[Phone removed]", released)

if not root.xpath('//h1'):
	title = root.xpath('//div[@class="sectionheader"]')[0].text.strip()
else:
	title = root.xpath('//h1')[0].text.strip()
year = re.search("20[0-9]{2}", root.xpath('//title')[0].text.strip()).group(0)

pdf_filename = year + "-" + title.replace(" ", "-").replace("---", "-").replace("$", "").replace(",", "").replace("/", "").replace("?", "").replace("\"", "").replace(":", "").lower() + ".txt"
with open(os.path.join("releases", pdf_filename), "w", encoding="latin1") as output:
	output.write(redacted)
with open(os.path.join("titles", pdf_filename), "w") as title_output:
	title_output.write(title) 
import html
from itertools import islice
import re
import sys
from bs4 import BeautifulSoup
from markdownify import MarkdownConverter


import ebooklib
from ebooklib import epub

from bionic_reading import BionicReading
from bionic_reading.settings import StopWordsBehavior, RareBehavior, Colors

def md(soup, **options):
    return MarkdownConverter(**options).convert_soup(soup)

def parse_html_string(s):

    soup = BeautifulSoup(s, 'html.parser')

    return soup


fixation = 0.7
saccades = 0.9
opacity = 0.8
stopwords = 0.7
stopwords_behavior = StopWordsBehavior.IGNORE.value.lower()
rare_words_behavior = RareBehavior.UNDERLINE.value.lower()
rare_words_max_freq = 2
highlight_color = Colors.RED.value.lower()

book = epub.read_epub(sys.argv[1], {'ignore_ncx': True})

bionic = BionicReading(
    fixation=fixation,
    saccades=saccades,
    opacity=opacity,
    stopwords=stopwords,
    stopwords_behavior=stopwords_behavior,
    output_format="html",
    rare_words_behavior=rare_words_behavior,
    rare_words_max_freq=rare_words_max_freq,
    highlight_color=highlight_color
)


documents = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
h = str()
processed = []
for x in islice(documents, 2):
    body = x.get_body_content()
    try:
        html_soup = parse_html_string(body)
        body = html_soup.find('body')

        text = body.get_text(separator="\n", strip=True)
        h = f'{h}\n{text}'
        processed.append(html_soup)
    except Exception as e:
        print(e)

try:
    tokens = bionic.split_text_to_words(h)

    text = bionic.tokenize(h)
    pairs = [(tk, tt) for (tk, tt) in zip(tokens, text)]
    pairs_it = iter(pairs)

    #for x in processed:
    x = processed[0]
    try:
        while True:

            original = str()
            replacement = str()

            pair = next(pairs_it, None)

            while pair != None and pair[0] != '\n':
                original = f'{original}{pair[0]}'
                replacement = f'{replacement}{pair[1]}'
                pair = next(pairs_it, None)

            pattern = re.compile((re.escape(original)))
            body_it = x.find(string=pattern)
            if body_it != None:
                replacement = re.sub(pattern, replacement, body_it.string)
                body_it.replace_with(BeautifulSoup(replacement, "html.parser"))
            else:
                break
        print(x)
    except Exception as e:
        print(e)
except Exception as e:
    print(e)
    
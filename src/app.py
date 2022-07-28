import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET

import spacy
nlp = spacy.load("en_core_web_sm")

from spacy.matcher import PhraseMatcher


def load_vocab(filepath):
    # vocab = pd.read_csv("../app/Vocab.csv")
    vocab = pd.read_csv(filepath)
    print(vocab.head())
    return vocab


def get_unique_categories(vocab):
    return vocab.Category.unique()


def phrase_matcher(categories, vocab):
    for category in categories:
        matcher = PhraseMatcher(nlp.vocab)
        phrase_list = vocab.loc[vocab['Category'] == category].Phrase
        # print(phrase_list)
        phrase_patterns = [nlp(text) for text in phrase_list]
        # print(phrase_patterns)
        matcher.add('TerminologyList', phrase_patterns)
        matches = matcher(doc)
        print(matches)
        for match_id, start, end in matches:
            span = doc[start:end]
            print(span.text)


tree = ET.parse('../app/responseXML')
root = tree.getroot()

phrase_to_process = "initial"

for elem in root.iter('BrightAll'):
	for e in elem.iter('PublicRemarks'):
		# print(e.text)
		phrase_to_process = e.text.lower()


print("\n\nPHRASE TO PROCESS: \n", phrase_to_process, "\n\n")
doc = nlp(phrase_to_process)

vocab = load_vocab("../app/Vocab.csv")
categories = get_unique_categories(vocab)

phrase_matcher(categories, vocab)

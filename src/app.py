from socket import SO_VM_SOCKETS_BUFFER_MIN_SIZE
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

import spacy
nlp = spacy.load("en_core_web_sm")

from spacy.matcher import PhraseMatcher

listing_xml = '../app/4680Whitely_MLSListing'
vocab_csv = "../app/Vocab2.csv"


def load_vocab(filepath):
    # vocab = pd.read_csv("../app/Vocab.csv")
    vocab = pd.read_csv(filepath)
    print(vocab)
    return vocab


def get_unique_categories(vocab):
    return vocab.Category.unique()


def phrase_matcher(categories, vocab, doc):
    for category in categories:
        matcher = PhraseMatcher(nlp.vocab, attr='LEMMA')
        phrase_list = vocab.loc[vocab['Category'] == category].Phrase
        # print(phrase_list)
        phrase_patterns = [nlp(text) for text in phrase_list]
        # print(phrase_patterns)
        matcher.add('TerminologyList', phrase_patterns)
        matches = matcher(public_remarks_doc)
        print(matches)
        for match_id, start, end in matches:
            span = doc[start:end]
            print(span.text)

def get_public_remarks():
    tree = ET.parse(listing_xml)
    root = tree.getroot()

    phrase_to_process = "initial"

    for elem in root.iter('BrightAll'):
        for e in elem.iter('PublicRemarks'):
            # print(e.text)
            phrase_to_process = e.text.lower()
    return phrase_to_process

def search_room_types_etree():
    tree = ET.parse(listing_xml)
    root = tree.getroot()

    room_types = []

    # for element in root.findall('BrightAll/*Remarks'):
    #     print(element.tag)
    #     room_types.append(element.tag)
    #     for e in element.iter():
    #         print(e.tag)

    # test = list(root.iterfind('*Remarks'))
    # for i in test:
    #     print(i)

    # if the current element is BrightAll, keep iterating 

    all_descendants = list(root.iter())
    print(all_descendants)

    for element in tree.findall('*/*Remarks'):
        print(element.tag)
        room_types.append(element.tag)
    return room_types

def search_room_types_beautifulsoup():
    print("beautiful soup")
    with open(listing_xml) as fp:
        soup = BeautifulSoup(fp, 'lxml-xml')
    print(soup.prettify())
    interior_features = soup.find_all("InteriorFeatures")


phrase_to_process = get_public_remarks()
print("\n\nPHRASE TO PROCESS: \n", phrase_to_process, "\n\n")
public_remarks_doc = nlp(phrase_to_process)

# rooms = search_room_types_etree()
rooms = search_room_types_beautifulsoup()
print(rooms)

vocab = load_vocab(vocab_csv)
categories = get_unique_categories(vocab)
print(categories)

phrase_matcher(categories, vocab, public_remarks_doc)

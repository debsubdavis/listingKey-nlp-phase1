from socket import SO_VM_SOCKETS_BUFFER_MIN_SIZE
import numpy as np
import pandas as pd
import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

import spacy
nlp = spacy.load("en_core_web_sm")

from spacy.matcher import PhraseMatcher

listing_xml = '../app/4680Whitely_MLSListing'
vocab_csv = "../app/Vocab.csv"
xml_search_json = '../app/xml_search_terms.json'


class Search:
    def __init__(self, name, xml_search_terms, categories):
        self.name = name
        self.xml_search_terms = xml_search_terms
        self.categories = categories
        self.phrases = [] # based on parsing the MLS Listing XML for the search terms

class Listing:
	def __init__(self, full_street_address, city, county, postal_code, latitude, longitude):
		self.full_street_address = full_street_address

def load_vocab(filepath):
    # vocab = pd.read_csv("../app/Vocab.csv")
    vocab = pd.read_csv(filepath)
    # print(vocab)
    return vocab


def get_unique_categories(vocab):
    return vocab.Category.unique()


def phrase_matcher(category, vocab, doc):
  
    matcher = PhraseMatcher(nlp.vocab, attr='LEMMA')
    # print("****Printing vocab.Category", vocab['Category'] == category)
    phrase_list = vocab.loc[vocab['Category'] == category].Phrase
    # print("*****PRINTING PHRASE LIST*****")
    # for t in phrase_list:
    #     print(t)
    phrase_patterns = [nlp(text) for text in phrase_list]
    print("\nPHRASE PATTERNS FROM VOCAB.CSV: ", phrase_patterns, "\nFOR CATEGORY: ", category)
    matcher.add('TerminologyList', phrase_patterns)
    matches = matcher(doc)
    # print(matches)
    # for match_id, start, end in matches:
    #     span = doc[start:end]
    #     print(span.text)
    return matches


def make_the_soup():
	with open(listing_xml) as fp:
		soup = BeautifulSoup(fp, 'lxml-xml')
		# print(soup.prettify())
	fp.close()
	return soup

def search_beautifulsoup(search_phrase, soup):
    search_result = soup.find_all(search_phrase)

    for s in search_result:
        # print("s in search_result", s.get_text())
        return s.get_text()


def get_listing_address(soup):

	full_street_address = search_beautifulsoup("FullStreetAddress", soup)
	city = search_beautifulsoup("City", soup)
	county = search_beautifulsoup("County", soup)
	postal_code = search_beautifulsoup("PostalCode", soup)
	postal_code_plus4 = search_beautifulsoup("PostalCodePlus4", soup)
	latitude = search_beautifulsoup("Latitude", soup)
	longitude = search_beautifulsoup("Longitude", soup)

	print(full_street_address, "-->", city, "-->", county, "-->", postal_code, "-->", postal_code_plus4, "-->", latitude, "-->", longitude )

def xml_searches(xml_search_filepath, vocab, soup):
	with open(xml_search_filepath, 'r') as f:
		data = json.load(f)

	f.close()
	xml_searches = []

	for i in data:
		name = i
		# print(name)
		xml_search_terms = data[name]['xml_search_terms']
		# print(search_terms)
		categories = data[name]['categories']
		# print(categories)
		search = Search(name, xml_search_terms, categories)
		# print(s.name, "-->", s.search_terms, "-->", s.categories)
		xml_searches.append(search)

	for s in xml_searches:
		# print(s.name, "-->", s.search_terms, "-->", s.categories)

		for term in s.xml_search_terms:
			print("\n\n***FIND IN XML FOR MLS LISTING: ", term)
			doc = nlp(search_beautifulsoup(term, soup))
			print("\nTEXT FROM MLS LISTING: \n", doc)

			# print("\n\nStarting Category\n")
			
			for category in s.categories:
				print("\nCATEGORY FOR PHRASE MATCHER: ", category)
				# v = load_vocab(vocab_csv)
				matches = phrase_matcher(category, vocab, doc)
				for match_id, start, end in matches:
					print("\nMATCH: ")
					span = doc[start:end]
					print(span.text)


vocab = load_vocab(vocab_csv)
categories = get_unique_categories(vocab)

soup = make_the_soup()
get_listing_address(soup)

xml_searches(xml_search_json, vocab, soup)


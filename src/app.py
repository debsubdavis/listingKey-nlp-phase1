from socket import SO_VM_SOCKETS_BUFFER_MIN_SIZE
from types import CoroutineType
import numpy as np
import pandas as pd
import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

import spacy
nlp = spacy.load("en_core_web_sm")

from spacy.matcher import Matcher

listing_xml = '../app/4680Whitely_MLSListing'
vocab_csv = "../app/Vocab.csv"
xml_search_json = '../app/xml_search_terms.json'
rooms_search_json = '../app/rooms_search_terms.json'


class Search:
    def __init__(self, name, xml_search_terms, categories):
        self.name = name
        self.xml_search_terms = xml_search_terms
        self.categories = categories
        self.phrases = [] # based on parsing the MLS Listing XML for the search terms

class Listing:
    def __init__(self, full_street_address, city, county, postal_code, latitude, longitude):
        self.full_street_address = full_street_address
        self.city = city
        self.county = county
        self.postal_code = postal_code
        self.latitude = latitude
        self.longitude = longitude
        self.rooms = []

class Room:
    def __init__(self, listing_id, room_type, api_url, request_body):
        self.listing_id = listing_id
        self.room_type = room_type
        self.api_url = api_url
        self.request_body = request_body

def load_vocab(filepath):
    # vocab = pd.read_csv("../app/Vocab.csv")
    vocab = pd.read_csv(filepath)
    # print(vocab)
    return vocab


def get_unique_categories(vocab):
    return vocab.Category.unique()


def phrase_matcher(column_name, col_search_value, vocab, doc):
  
    matcher = Matcher(nlp.vocab)
    # print("****Printing vocab.Category", vocab['Category'] == category)
    phrase_list = vocab.loc[vocab[column_name] == col_search_value].Phrase
    # print("*****PRINTING PHRASE LIST*****")
    # for t in phrase_list:
    #     print(t)
    # phrase_patterns = [nlp(text) for text in phrase_list]
    phrase_patterns = []
    for text in phrase_list:
        space_positions = []
        for pos, char in enumerate(text):
            if(char == " "):
                space_positions.append(pos)
        # print("space_positions", space_positions)
        new_pattern = []
        # print("len of space-positions: ", len(space_positions))

        if len(space_positions) == 0:
            new_pattern.append({"LEMMA":text})
        for i in range(len(space_positions)):

            if len(space_positions) == 1:
                word = text[:space_positions[i]]
                # print("word: ", word)
                new_pattern.append({"LEMMA": word})
                # new_pattern.append({"IS_PUNCT": True})
                word2 = text[space_positions[i]+1:]
                # print("word2: ", word2)
                new_pattern.append({"LEMMA": word2})
            else:
  
                if i + 1 == len(space_positions):
                    word = text[space_positions[i-1]:space_positions[i]]
                    # print("word in else, last iteration: ", word)
                    new_pattern.append({"LEMMA": word})
                    word2 = text[space_positions[i]+1:]
                    # print("word2 in else: ", word2)
                    # new_pattern.append({"IS_PUNCT": True})
                    new_pattern.append({"LEMMA":word2})
                else:
                    if i == 0:
                        word = text[:space_positions[i]]
                    else:
                        word = text[space_positions[i-1]:space_positions[i]]
                    new_pattern.append({"LEMMA": word})
                    # new_pattern.append({"IS_PUNCT": True})

        print(new_pattern)


        phrase_patterns.append(new_pattern)

    # print("\nPHRASE PATTERNS FROM VOCAB.CSV: ", phrase_patterns, "\nFOR CATEGORY: ", col_search_value)
    # for pattern in phrase_patterns:
    #     print("pattern", pattern)
    matcher.add('TerminologyList', phrase_patterns)
    # print("&&&&&&&doc in phrase-matcher", doc)
    # for token in doc:
    #     print(token)
    matches = matcher(doc)
    # print("@@@@@Printing MATCHES")
    # print(matches)
    for match_id, start, end in matches:
        span = doc[start:end]
        print(span.text)
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
        print(i)
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

        for term in s.xml_search_terms:
            print("\n\n***FIND IN XML FOR MLS LISTING: ", term)
            doc = nlp(search_beautifulsoup(term, soup))
            print("\nTEXT FROM MLS LISTING: \n", doc)
            
            for category in s.categories:
                print("\nCATEGORY FOR PHRASE MATCHER: ", category)
                # v = load_vocab(vocab_csv)
                matches = phrase_matcher("Category", category, vocab, doc)
                for match_id, start, end in matches:
                    print("\nMATCH: ")
                    print("testing")
                    span = doc[start:end]
                    print(span.text)
                    print("category: ", category)

def load_rooms_json(url_path):

    with open(url_path, 'r') as f:
        data = json.load(f)
    
    f.close()
    print("PRINTING data IN load_rooms_json")
    print(data)
    return data


def create_kitchen(listing_id, soup, json_data):
    print("inside create_kitchen")

    print("PRINTING json_data inside create_kitchen")
    print(json_data)
    # print("\nprinting json_data.rooms")
    # print(json_data["Rooms"])

    for room in json_data["Rooms"]:

        if room["name"] == 'Kitchen':
            print(room["name"])
            print(room["xml_searches"])
            print(len(room["xml_searches"]))
            for search in room["xml_searches"]:
                search_term = search['xml_search_term']
                print("\nSEARCH***",search_term)
                doc_result = nlp(search_beautifulsoup(search_term, soup))
                print(doc_result)
                print("subcategories: ", len(search['subcategories']))
                for subcategory in search['subcategories']:
                    print("****SUBCATEGORY***", subcategory)
                    matches = phrase_matcher("SubCategory", subcategory , vocab, doc_result)
                    for match_id, start, end in matches:
                        print("\nMATCH: ")
                        print("testing")
                        span = doc_result[start:end]
                        print(span.text)
    # int KitchenId
    # int ListingId
    #  string Description
    description = "Kitchen created through NLP parsing"
    # int? KitchenType

    # search_beautifulsoup("InteriorFeatures", soup)
    # string KitchenLastUpgrade
    # FloorLevelEnum? KitchenFloorLevel
    # (BasementLowest = 1, First = 2, Second = 3, Third = 4, FourthAttic = 5)

    # KitchenAmentitiesSelected []



    # (Island = 106, CeilingFan = 107, WalkInPantry = 108, DoubleSink = 109, Backsplash = 110, BreakfastRoom = 111)
    # KitchenFlooringSelected []
    # (Concrete = 1, Stone = 2, Tile = 3, Carpet = 4, VinylLinoleum = 5, WoodOak = 6, WoodLaminate = 7, WoodMaple = 8, WoodWalnut = 9, WoodPine = 10, WoodEngineered = 11)


    # KitchenCountertopsSelected []
    # (Granite = 13, Quartz = 14, Laminate = 15, Concrete = 16, RecycledGlass = 17, Marble = 18, Quartzite = 19)

    # keys = ["KitchenAmentitiesSelected", "KitchenCountertopsSelected"]
    # values = []

    # dicts = {}

    # for i in range (len(keys)):
    #     dicts[keys[i]] = values[i]
    # print(dicts)



vocab = load_vocab(vocab_csv)
categories = get_unique_categories(vocab)

soup = make_the_soup()
get_listing_address(soup)

# xml_searches(xml_search_json, vocab, soup)
json_data = load_rooms_json(rooms_search_json)
create_kitchen("123456", soup, json_data)



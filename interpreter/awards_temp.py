import json
import re
from collections import Counter

import en_core_web_md
import imdb
import nltk
from nltk import edit_distance
import spacy
#from imdb_api import imdb_get_similar
import utilities

spacy.load('en_core_web_md')
nltk.download('punkt')


def find_awards(data, awards, year):

    nominees = {award: [] for award in awards}
    # Track number of times each potential nominee is mentioned for each award
    filtered_data = filter_data(data)

    functs_to_map = [utilities.remove_punctuation,
                     utilities.lower, 
                     utilities.remove_stop_words, 
                     utilities.stem]
    preprocessed_tweets = preprocess_tweets(filtered_data, functs_to_map)

   # ia = imdb.IMDb()

    # Load NER tagger
    nlp = en_core_web_md.load()

  #  allowed_labels = {'PERSON', 'WORK_OF_ART', 'EVENT', 'ORGANIZATIONS', 'PRODUCT','LANGUAGE'}
    allowed_labels = {'PERSON', 'WORK_OF_ART', 'EVENT', 'ORGANIZATIONS', 'NORP', 'GPE', 'LOCATION', 'PRODUCT'}

    res = []
    for tweet in preprocessed_tweets:
        
        tagged_text = list(map(nlp, tweet))
        likely_award_chunks = [chunk.text for seq in tagged_text for chunk in seq.ents if chunk.label_ in allowed_labels ]
        counter = Counter(filter(bool, likely_award_chunks))
        if len(counter): res.extend([ item[0] for item in counter.most_common(1) ])

    return res


def filter_data(data):
    text_lst = [post['text'] for post in data]
    with open('./interpreter/patterns/awards_patterns.json', 'r') as f:
        patterns = json.load(f)
    text_lst = [re.sub('|'.join(patterns['remove_patterns']), '', text, flags=re.IGNORECASE) for text in text_lst]
    # Filter posts that contain none of the negative match tokens and any of the positive match tokens
    # all the posts have none of the negatives and at least one positive
    return [seq for seq in text_lst if not any(word in seq for word in patterns['negative_patterns']) and any(
        word in seq for word in patterns['positive_patterns'])]


def preprocess_awards_for_similarity(awards, functs_to_map):
    mod_awards = [award.replace('best', '').replace('award', '').strip() for award in awards]
    for func in functs_to_map:
        mod_awards = map(func, mod_awards)
    return dict(zip(awards, list(mod_awards)))

def preprocess_post_for_similarity(post, functs_to_map):
    for func in functs_to_map:
        post = func(post)
    return post

def get_relevant_award(post, awards):
    return max(awards, key=lambda key: similarity_metric(post, awards[key]))

def similarity_metric(post, award):
    num_common_tokens = len(set(post).intersection(set(award)))
    return num_common_tokens / len(award)

# def preprocess_tweets(awards, functs_to_map):
#     mod_awards = [award.replace('best', '').replace('award', '').strip() for award in awards]
#     for func in functs_to_map:
#         mod_awards = map(func, mod_awards)
#     return dict(zip(awards, list(mod_awards)))

def preprocess_tweets(tweets, funcs):
    for func in funcs:
        tweets = map(func, tweets)
    return list(tweets)








# s = 'Timothee Chalamet totally deserved to win Best Actor! He is the loml.'
# nlp = en_core_web_md.load()

# for chunk in nlp(s).ents:
#     print(chunk.text, chunk.label_)
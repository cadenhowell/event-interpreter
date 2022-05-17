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


def find_nominees(data, awards, year):

    nominees = {award: [] for award in awards}
    # Track number of times each potential nominee is mentioned for each award
    nominee_tracker = {award: Counter() for award in awards}

    filtered_data = filter_data(data)

    functs_to_map = [utilities.remove_punctuation,
                     utilities.lower, 
                     utilities.remove_stop_words, 
                     utilities.stem]
    preprocessed_awards = preprocess_awards_for_similarity(awards, functs_to_map)

   # ia = imdb.IMDb()

    # Load NER tagger
    nlp = en_core_web_md.load()

    allowed_labels = {'PERSON', 'WORK_OF_ART', 'EVENT', 'ORGANIZATIONS', 'PRODUCT','LANGUAGE'}

    for award in preprocessed_awards:
        matches = [match[0] for match in extractBests(award, text_lst, limit=50)]
        for nominee in nominees[award]:
            candidates = [candidate[0] for candidate in extractBests(nominee, matches, limit=25)]
        
        tagged_text = list(map(nlp, candidates))
        likely_winners = [chunk.text for seq in tagged_text for chunk in seq.ents if chunk.label_ in allowed_labels ]
        counter = Counter(likely_winners)

        # Keep logic in case of arbitrary selection, multiple names
        winner[award] = [item[0] for item in counter.most_common(1)]

    return winner

    for post in filtered_data:

        # Tag post with named entities
        ner_tagged_post = nlp(post)

        # Get all named entity chunks
        likely_nominees = [chunk.text.lower() for chunk in ner_tagged_post.ents]

        for nominee in likely_nominees:
            preprocessed_post = preprocess_post_for_similarity(post, functs_to_map)

            # Assign post to most likely award or None if none likely
            award = get_relevant_award(preprocessed_post, preprocessed_awards)

            # Increment nominee counter
            if award:
                nominee_tracker[award][nominee] += 1

    for award, nominee_tracker in nominee_tracker.items():
        for likely_nominee in nominee_tracker.keys():
            if len(nominees[award]) == 5: break
            if any(token in award for token in ['actor', 'actress', 'director', 'producer', 'writer']):
                closest = imdb_get_similar(likely_nominee, ia, year, 'person')
            elif any(token in award for token in ['series', 'television']):
                closest = imdb_get_similar(likely_nominee, ia, year, 'tv series')
            else:
                closest = imdb_get_similar(likely_nominee, ia, year, 'movie')
            if closest and edit_distance(likely_nominee, closest) < 3:
                if closest not in nominees[award]:
                    nominees[award].append(closest)
                print(f'{closest} added to {award}')

    return nominees


def filter_data(data):
    text_lst = [post['text'] for post in data]
    with open('./interpreter/patterns/nominee_patterns.json', 'r') as f:
        patterns = json.load(f)
    text_lst = [re.sub('|'.join(patterns['remove_patterns']), '', text, flags=re.IGNORECASE) for text in text_lst]
    # Filter posts that contain none of the negative match tokens and any of the positive match tokens
    # all the posts have none of the negatives and at least one positive
    return [seq for seq in text_lst if not any(word in seq for word in patterns['negative_patterns']) and any(
        word in seq for word in patterns['positive_patterns'])]


def preprocess_awards_for_similarity(awards, functs_to_map):
    # mod_awards = [award.replace('best', '').replace('award', '').strip() for award in awards]
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
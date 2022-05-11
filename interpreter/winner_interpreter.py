from collections import Counter

import spacy

import utilities

spacy.load('en_core_web_sm')
import en_core_web_sm
from thefuzz.process import extractBests


def find_winner(data, awards, nominees):
    winner = {}

    text_lst = _preprocess(data)
    nlp = en_core_web_sm.load()

    for award in awards:
        matches = [match[0] for match in extractBests(award, text_lst, limit=50)]
        for nominee in nominees[award]:
            candidates = [candidate[0] for candidate in extractBests(nominee, matches, limit=25)]
        
        tagged_text = list(map(nlp, candidates))
        allowed_labels = ['PERSON', 'WORK_OF_ART', 'EVENT', 'ORGANIZATIONS', 'NORP', 'GPE', 'LOCATION', 'PRODUCT']
        likely_winners = [chunk.text for seq in tagged_text for chunk in seq.ents if chunk.label_ in allowed_labels ]
        counter = Counter(likely_winners)

        # Keep logic in case of arbitrary selection, multiple names
        winner[award] = [item[0] for item in counter.most_common(1)]

    return winner

def _preprocess(data):
    text_lst = [post['text'] for post in data]
    search_words = ['winner','won', 'wins']
    text_lst = [seq for seq in text_lst if any(word in seq for word in search_words)]
    text_lst = utilities.remove_punctuation(text_lst)
    return text_lst
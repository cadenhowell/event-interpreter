import json
import re
from collections import Counter

import en_core_web_md
import imdb
import nltk
import spacy
import random
from nltk import edit_distance

import utilities
from imdb_api import imdb_get_similar

spacy.load('en_core_web_md')
nltk.download('punkt')


def find_nominees(data, awards, year):
    nominees = {award: [] for award in awards}
    possible_nominees = {award: Counter() for award in awards}

    with open('./interpreter/patterns/nominee_patterns.json', 'r') as f:
        patterns = json.load(f)

    posts = filter_format_data(
        data, 
        patterns["preprocess_positive_patterns"], 
        patterns["preprocess_negative_patterns"], 
        patterns["preprocess_remove_patterns"]
    )

    preprocessed_awards = preprocess_awards_for_similarity(
        awards, 
        patterns["similarity_award_remove_patterns"],
        patterns["similarity_award_synonyms"]
    )
    preprocessed_posts = preprocess_posts_for_similarity(
        posts, 
        patterns["similarity_post_remove_patterns"]
    )

    ia = imdb.IMDb()
    nlp = en_core_web_md.load()

    for post, preprocessed_post in zip(posts, preprocessed_posts):
        award = get_relevant_award(preprocessed_post, preprocessed_awards)
        if not award: continue

        ner_tagged_post = nlp(post)
        likely_nominees = [chunk.text.lower() for chunk in ner_tagged_post.ents]
        if not likely_nominees: continue

        for nominee in likely_nominees:
            if nominee not in award:
                possible_nominees[award][nominee] += 1
        # if random.random() < 0.05:
        #     print(post)
        #     print(award)
        #     print(likely_nominees)
        #     print("\n")
    for key, value in possible_nominees.items():
        print(key, value, "\n")
    for award, possible_nominees in possible_nominees.items():
        for likely_nominee, _ in possible_nominees.most_common():
            if len(nominees[award]) == 1:
                break
            if any(token in award for token in ['actor', 'actress', 'director', 'producer', 'writer']):
                closest = imdb_get_similar(likely_nominee, ia, year, 'person')
            elif any(token in award for token in ['series', 'television']):
                closest = imdb_get_similar(
                    likely_nominee, ia, year, 'tv series')
            elif any(token in award for token in ['movie', 'film', 'motion picture']):
                closest = imdb_get_similar(likely_nominee, ia, year, 'movie')
            else:
                closest = imdb_get_similar(likely_nominee, ia, year, 'person')
            if closest and edit_distance(likely_nominee, closest) < 3:
                if closest not in nominees[award]:
                    nominees[award].append(closest)
                print(f'{closest} added to {award}')

    return nominees


def filter_format_data(data, positive_patterns, negative_patterns, patterns_to_remove):
    text_lst = [post['text'] for post in data]
    text_lst = remove_patterns(text_lst, patterns_to_remove)
    return [seq for seq in text_lst if
            not any(re.search(pattern, seq, flags=re.I) for pattern in negative_patterns)
            and any(re.search(pattern, seq, flags=re.I) for pattern in positive_patterns)]


def preprocess_awards_for_similarity(awards, patterns_to_remove, synonym_patterns):
    functs_to_map = [utilities.remove_punctuation,
                     utilities.lower,
                     utilities.remove_stop_words,
                     utilities.stem]
    mod_awards = simplify(awards, functs_to_map, patterns_to_remove)
    mod_awards = dict(sorted(zip(awards, mod_awards), key = lambda award: len(award[1])))
    mod_synonyms = simplify(synonym_patterns, [utilities.stem])
    return {key: [get_synonyms(token, mod_synonyms) for token in value] for key, value in mod_awards.items()}


def preprocess_posts_for_similarity(posts, patterns_to_remove):
    functs_to_map = [utilities.lower,
                     utilities.stem]
    return simplify(posts, functs_to_map, patterns_to_remove)


def simplify(seq_lst, functs_to_map, patterns_to_remove=None):
    mod_seq_lst = remove_patterns(seq_lst, patterns_to_remove) if patterns_to_remove else seq_lst
    for func in functs_to_map:
        mod_seq_lst = map(func, mod_seq_lst)
    return list(mod_seq_lst)


def get_synonyms(token, patterns):
    for pattern in patterns:
        l_pattern = utilities.lower(pattern)
        if token in l_pattern:
            return l_pattern
    return [token]


def remove_patterns(seq_lst, patterns):
    regex = re.compile('|'.join(patterns), flags=re.I)
    mod_seq_lst = [re.sub(regex, '', seq).strip() for seq in seq_lst]
    return mod_seq_lst


def get_relevant_award(post, awards):
    best_award = max(awards, key=lambda key: similarity_metric(post, awards[key]))
    return best_award if similarity_metric(post, awards[best_award]) > 0 else None


def similarity_metric(post, award):
    common_tokens = 0
    for synonym_group in award:
        if any([token in post for token in synonym_group]):
            common_tokens += 1
    return common_tokens

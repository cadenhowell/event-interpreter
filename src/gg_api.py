'''Version 0.35'''
import json
import os.path
import time

import nltk

from interpreters import (awards_interpreter, host_interpreter,
                          nominee_interpreter, presenter_interpreter, people_sentiment_analyzer)

OFFICIAL_AWARDS = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']


def _fetch_data(year):
    '''Load data to global variable so each function does not need to reload it'''
    if 'data' not in globals():
        global data
        data = {}
    if year not in data:
        file = open(os.path.dirname(__file__) + f'/../data/gg{year}.json')
        data[year] = json.load(file)
    return data[year]

def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    loaded_data = _fetch_data(year)
    hosts = host_interpreter.find_host(loaded_data)
    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    loaded_data = _fetch_data(year)
    awards = awards_interpreter.find_awards(loaded_data, year)
    return awards

def _get_nominees_and_winners(year):
    loaded_data = _fetch_data(year)
    if 'naw' not in globals():
        global naw
        naw = {}
    if year not in naw:
        naw[year] = nominee_interpreter.find_nominees(loaded_data, OFFICIAL_AWARDS, year)
    return naw[year]

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    naw = _get_nominees_and_winners(year)
    nominees = {k: v[1:] for k, v in naw.items()}
    for award in OFFICIAL_AWARDS:
        if award not in nominees:
            nominees[award] = ''
    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    naw = _get_nominees_and_winners(year)
    winners = {k: (v[0] if len(v) > 0 else '') for k, v in naw.items()}
    for award in OFFICIAL_AWARDS:
        if award not in winners:
            winners[award] = ''
    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    loaded_data = _fetch_data(year)
    presenters = presenter_interpreter.find_presenters(loaded_data, OFFICIAL_AWARDS, year)
    for award in OFFICIAL_AWARDS:
        if award not in presenters:
            presenters[award] = ''
    return presenters

def get_sentiment_comparison(year, people_list):
    loaded_data = _fetch_data(year)
    sentiment_dict = people_sentiment_analyzer.analyze_people(people_list, loaded_data)
    return sentiment_dict

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    dir = os.path.dirname(__file__) + '/../env/nltk_downloads'
    nltk.data.path.append(dir)
    nltk.download('punkt', download_dir=dir)
    nltk.download('stopwords', download_dir=dir)
    nltk.download('averaged_perceptron_tagger', download_dir=dir)
    nltk.download('maxent_ne_chunker', download_dir=dir)
    nltk.download('words', download_dir=dir)
    print("Pre-ceremony processing complete.")
    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    start = time.time()
    pre_ceremony()
    years = ['2013', '2015']
    for year in years:
        hosts = get_hosts(year)
        print(f'{year} Hosts\n\n{hosts}\n\n')
        print(f'{year} Nominees\n\n{get_nominees(year)}\n\n')
        print(f'{year} Winners\n\n{get_winner(year)}\n\n')
        print(f'{year} Presenters\n\n{get_presenters(year)}\n\n')
        print(f'{year} Award names\n\n{get_awards(year)}\n\n')
        print(f'{year} Sentiment Analysis of Hosts\n\n{get_sentiment_comparison(year, hosts)}')
    finish = time.time()
    print(f'Elapsed time: {(finish - start) / 60} minutes')
    return

if __name__ == '__main__':
    main()

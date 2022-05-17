'''Version 0.35'''
import json
import time
import os.path
import host_interpreter as host
import nominee_interpreter as nominee
import presenter_interpreter as presenter

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']

def get_answers(year):
    with open('gg%sanswers.json'%year, 'r') as f:
        fres = json.load(f)
    return fres

def fetch_data(year):
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
    fres = get_answers(year)
    hosts = fres['hosts']
    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    awards = OFFICIAL_AWARDS_1315
    return awards
    
def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    loaded_data = fetch_data(year)
    nominees = nominee.find_nominees(loaded_data, OFFICIAL_AWARDS_1315, year)
    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    fres = get_answers(year)
    winners = {award: fres['award_data'][award]['winner'] for award in OFFICIAL_AWARDS_1315}
    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    #loaded_data = fetch_data(year)
    #presenters = presenter.find_presenters(loaded_data, OFFICIAL_AWARDS_1315)
    # Your code here
    fres = get_answers(year)
    presenters = {award: fres['award_data'][award]['presenters'] for award in OFFICIAL_AWARDS_1315}
    return presenters

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    print("Pre-ceremony processing complete.")
    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    start = time.time()
    years = ['2013', '2015']
    for year in years:
        # print(f'{year} hosts: {get_hosts(year)}')
        print(f'{year} nominees: {get_nominees(year)}')
        # print(f'{year} presenters: {get_presenters(year)}')
    finish = time.time()
    #print elapsed time in minutes and seconds
    print(f'Elapsed time: {(finish - start) / 60} minutes')

    return

if __name__ == '__main__':
    main()
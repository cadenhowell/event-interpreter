from collections import Counter
import re
import utilities
import json
import nltk
nltk.download('punkt')

def increment_award_presenter(award_dict, award, name, val):
    #print('incrementing name', name)
    if name not in award_dict[award]:
        award_dict[award][name] = val
    else:
        award_dict[award][name] += val

def has_presenter_words(t_split):
    result = []
    if 'presented' in t_split:
        result.append('presented')
    if 'presents' in t_split:
        result.append('presents')
    if 'presenting' in t_split:
        result.append('presenting')
    if 'present' in t_split:
        result.append('present')
    return result

def no_uncertain_words(t_split):
    return all(['should' not in t_split, 'wish' not in t_split, 'would' not in t_split])

def find_matched_awards(awards, t_split, winners_dict):
    max_weight = 0
    matched_award = None
    # check for similar award names
    for award_vector in awards:
        award_no_stop = award_vector[1]
        weight = 0
        for word in award_no_stop:
            if word in t_split:
                weight += 1
        if weight >= int(len(award_no_stop) / 2) and weight > max_weight:
            max_weight = weight
            matched_award = award_vector
    if matched_award != None:
        return matched_award
    # if no award matched by award name, try by winner name
    for winner_name, award_and_relation in winners_dict.items():
        if winner_name in t_split:
            pass
    
    return None

def backward_check_for_names_from_index(index, t_split, dense_t_split, tl_split_lower, award_dict, matched_award):
    #look for single presenter
    start_index = index + 1
    name1_list = []
    name1_list_caps = []
    # TODO: CONTINUE CHECKING AFTER FINDING ONE GUY, STOP CHECK AT ANY FORM OF PUNCTUATION
    while start_index >= 0:
        start_index -= 1
        start_word = t_split[start_index]
        if start_word not in dense_t_split: continue

        temp_index = start_index
        while temp_index >= 0 and t_split[temp_index] in dense_t_split:
            # check for odd cases
            new_word = t_split[temp_index]
            if name1_list != []:
                if name1_list_caps[0][0].isupper() and name1_list_caps[0][1].islower():
                    if len(new_word) > 1:
                        if new_word[0].islower() or new_word[1].isupper():
                            break
            # check for non-alphabetical
            if not new_word.isalpha(): break

            # check for name length
            if len(name1_list) > 2: break

            # check for name component length:
            if len(new_word) < 3: break

            # append new word
            name1_list.append(tl_split_lower[temp_index])
            name1_list_caps.append(new_word)
            temp_index -= 1
        
        name1_list.reverse()
        name1 = ""
        for word in name1_list:
            name1 += word + " "
        if name1 != "":
            name1 = name1[:-1]
            #print(name1)
            increment_award_presenter(award_dict, matched_award, name1, 2) 
        name1_list = []

def backward_check_for_names(tl_split_lower, t_split, award_dict, matched_award, dense_t_split, keyword):
        keyword_index = tl_split_lower.index(keyword)
        dense_t_split_lower = []
        for word in dense_t_split:
            dense_t_split_lower.append(word.lower())

        if keyword_index == 0: return
        #print(keyword)
        #print(dense_t_split)
        first_potential_nameword = dense_t_split[dense_t_split_lower.index(keyword) - 1]
        name1_index = t_split.index(first_potential_nameword)
        #name1_index = keyword_index - 1
        name2_index = None

        # if indicator of multiple presenters, look for multiple presenters
        bef_keyword_lower = tl_split_lower[0:name1_index]
        if ("amp" in bef_keyword_lower and bef_keyword_lower.index("amp") <= name1_index - 1):
            name2_index = bef_keyword_lower.index("amp")
        if ("and" in bef_keyword_lower and bef_keyword_lower.index("and") <= name1_index - 1):
            name2_index = bef_keyword_lower.index("and")

        if name2_index != None:
            #look for multiple presenters
            backward_check_for_names_from_index(name1_index, t_split, dense_t_split, tl_split_lower, award_dict, matched_award)
            backward_check_for_names_from_index(name2_index, t_split, dense_t_split, tl_split_lower, award_dict, matched_award)
        else:
            backward_check_for_names_from_index(name1_index, t_split, dense_t_split, tl_split_lower, award_dict, matched_award) 
        return

def process_presented(t_split, tl_split_lower, award_dict, matched_award):
    #print(t_split)
    dense_t_split = utilities.remove_stop_words(t_split)
    if "by" in t_split:
        name1_index = tl_split_lower.index("by") + 1
                        
        # if by is the last word, not useful, go to next post
        if not name1_index + 2 < len(tl_split_lower): return

        name_1 = t_split[name1_index].capitalize() + " " + t_split[name1_index + 1].capitalize()
        increment_award_presenter(award_dict, matched_award, name_1, 2)
    else:
        backward_check_for_names(tl_split_lower, t_split, award_dict, matched_award, dense_t_split, "presented")

        

def process_presenting(t_split, tl_split_lower, award_dict, matched_award):
    dense_t_split = utilities.remove_stop_words(t_split)
    backward_check_for_names(tl_split_lower, t_split, award_dict, matched_award, dense_t_split, "presenting")

def process_presents(t_split, tl_split_lower, award_dict, matched_award):
    dense_t_split = utilities.remove_stop_words(t_split)
    backward_check_for_names(tl_split_lower, t_split, award_dict, matched_award, dense_t_split, "presents")

def process_present(t_split, tl_split_lower, award_dict, matched_award):
    dense_t_split = utilities.remove_stop_words(t_split)
    backward_check_for_names(tl_split_lower, t_split, award_dict, matched_award, dense_t_split, "present")

def process_presenter(t_split, tl_split_lower, award_dict, matched_award):
    dense_t_split = utilities.remove_stop_words(t_split)
    backward_check_for_names(tl_split_lower, t_split, award_dict, matched_award, dense_t_split, "presenter")



def find_presenters(data, awards_official):
    # get awards and award_no_stop
    awards = [[awards_official[i], utilities.remove_stop_words(awards_official[i])] for i in range(len(awards_official))]

    # get winners
    file = open('gg2013answers.json')
    answers_data = json.load(file)
    award_data = answers_data["award_data"]
    winners_dict = {}
    for award, ans_dict in award_data.items():
        full_winner = ans_dict["winner"]
        winners_dict[full_winner] = [award, "full"]
        winner_subnames = full_winner.split(" ")
        if len(winner_subnames) <= 2:
            for subname in winner_subnames:
                if subname != "of": winners_dict[subname] = [award, "partial"]

    award_dict = dict()
    for award in awards:
        award_dict[award[0]] = dict()
    
    for post in data:
        tweet = re.sub(r'[^\w\s]', '', post['text'])
        t_lower = tweet.lower()
        t_split = tweet.split()
        tl_split_lower = t_lower.split()
        #if has presented by and does not have words that indicate inaccuracy
        presenter_indicators = has_presenter_words(tl_split_lower)
        if presenter_indicators != [] and no_uncertain_words(tl_split_lower):
            matched_award_vector = find_matched_awards(awards, t_split, winners_dict)
            if matched_award_vector == None: continue
            matched_award = matched_award_vector[0]
            #print(tweet)

            for present_word in presenter_indicators:
                if present_word == 'presented': process_presented(t_split, tl_split_lower, award_dict, matched_award)
                if present_word == 'presents': process_presents(t_split, tl_split_lower, award_dict, matched_award)
                if present_word == 'presenting': process_presenting(t_split, tl_split_lower, award_dict, matched_award)
                if present_word == 'present': process_present(t_split, tl_split_lower, award_dict, matched_award)
                if present_word == 'presenter': process_presenter(t_split, tl_split_lower, award_dict, matched_award)

    #for key, item in award_dict.items():
    #    print(key, item)
    result = utilities.awards_to_people_parser(award_dict)
    presenters = []
    return presenters
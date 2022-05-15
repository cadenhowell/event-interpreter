import string
from unittest import result 
import nltk
from nltk.corpus import stopwords
import imdb
import imdb_api
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

nltk.download('maxent_ne_chunker')
nltk.download('words')

def tokenize(str):
    return word_tokenize(str)

def format_return(seq, return_as_str):
    is_str = type(seq) is str

    if (return_as_str == is_str):
        return seq
    elif return_as_str and not is_str:
        return ' '.join(seq)
    else:
        return tokenize(seq)

def lower(seq, return_as_str=False):
    lower_str, lower_lst = None, None

    if type(seq) is str:
        lower_str = str.lower()
    else:
        lower_lst = list(map(str.lower(), seq))

    return format_return(lower_str or lower_lst, return_as_str)

def remove_stop_words(seq, return_as_str=False):
    if type(seq) is str:
        seq = tokenize(seq)

    stops = set(stopwords.words('english'))
    tokenized_no_sw = [token for token in seq if token not in stops]

    return format_return(tokenized_no_sw, return_as_str)

def stem(seq, return_as_str=False):
    if type(seq) is str:
        seq = tokenize(seq)

    ps = PorterStemmer()
    stemmed_lst = list(map(ps.stem(), seq))
    
    return format_return(stemmed_lst, return_as_str)

def remove_punctuation(seq, return_as_str=False):
    if type(seq) is str:
        seq = seq.translate(str.maketrans('', '', string.punctuation))
    else:
        seq = [token for token in seq if token not in string.punctuation]

    return format_return(seq, return_as_str)

def _increment_award_val(result_dict, key, val):
    if key not in result_dict:
        result_dict[key] = val
    else:
        result_dict[key] += val

def _increment_award_presenter(award_dict, award, name, val):
    if award not in award_dict:
        award_dict[award] = dict()
        award_dict[award][name] = val
    if name not in award_dict[award]:
        award_dict[award][name] = val
    else:
        award_dict[award][name] += val

def awards_to_people_parser(award_ppl_dict):
    nltk_dict = dict()
    ia = imdb.IMDb()
    result_dict = dict()
    correct_names_dict = dict()
    for award, people_dict in award_ppl_dict.items():
        if len(people_dict) == 0:
            result_dict[award] = ''
            continue

        sorted_people = sorted(people_dict.items(), key=lambda x: x[1], reverse=True)
        for item in sorted_people:
            name = item[0]
            val = item[1]
            # perform imdb check and value mutation

            found_name = imdb_api.imdb_get_similar_people(name, ia)
            num_nnp = 0
            if found_name == 0 or found_name == '': continue


            if found_name != 0:
                found_list = found_name.split(" ")
                uppercase_found_list = []
                for i in found_list:
                    var = i
                    uppercase_found_list.append(var.capitalize())
                name_list_uppercased = " ".join(uppercase_found_list)
                        
                # perform nltk check and value mutation
                if name in nltk_dict:
                    l1 = nltk_dict[name]
                else:
                    name_token = tokenize(name_list_uppercased)
                    l1 = nltk.pos_tag(name_token)
                    nltk_dict[name] = l1
                for element in l1:
                    if element[1] != 'NNP':
                        val = val * 0.25
                    else:
                        num_nnp += 1
            if num_nnp == 0: continue
            
            # if imdb marked it as a nickname, remove nickname marker
            if found_list[-1] == "nickname": 
                found_list.pop()
                new_found_list = []
                for element in found_list:
                    if element != '': new_found_list.append(element)
                found_list = new_found_list
                found_name = " ".join(new_found_list)
            
            # if good length for name, increase weight
            name_list = name.split(" ")
            if len(found_list) == len(name_list):
                if len(found_list) == 2:
                    val = val * 5
                    if found_list == name_list:
                        val = val * 5

            if found_name == name:
                if len(found_name) > 1:
                    val = val * 5
            else:
                for part in found_list:
                    if part == name:
                        val = val * 1.5
            _increment_award_presenter(correct_names_dict, award, found_name, val)

    #print(correct_names_dict)
    for award, person_dict in correct_names_dict.items():
        max_persons = [None, None]
        max_scores = [0, 0]
        for person, score in person_dict.items():
            if score > max_scores[0]:
                max_persons[1], max_scores[1] = max_persons[0], max_scores[0]
                max_persons[0], max_scores[0] = person, score
            elif score > max_scores[1]:
                max_persons[1], max_scores[1] = person, score
        
        if max_scores[0] > max_scores[1] / 4 and max_persons[1] != None and len(max_persons[0]) == len(max_persons[1]):
            result_dict[award] = max_persons
        else:
            result_dict[award] =  max_persons#[max_persons[0]]
    #print(result_dict)
    return result_dict
        #sort by value
        #check for whether or not word is nltktagged as NNP, not tagged as NNP --> .25x
        #if exact match for search term, add 5x value
        #if shared word with search term, 2x value


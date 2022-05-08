import string 

from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

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

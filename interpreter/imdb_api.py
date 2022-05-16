import imdb
import inspect
import re

# you will need to call 'var = imdb.IMDb() and pass var into get_imdb_check(entity, var) for it to have a db to reference
ia = imdb.IMDb()

def imdb_check_entity(entity, ia, date=None):
    return max(imdb_check_person(entity, ia, date), imdb_check_movie(entity, ia, date))

# returns 1 if found name match, 2 if found associated movie or tv show released on viable date
def imdb_check_person(person, ia, date):
    person = person.lower()
    person_results = ia.search_person(person)
    if person_results == []: return 0
    for index in range(min(len(person_results),2)):
        person_match = person_results[index]
        person_name = person_match.get('name').lower()

        if person_name != person:
            return 0

        ia.update(person_match, info=['release dates', 'filmography'])
        filmography = person_match.get('filmography')
        if len(filmography > 0):
            return 2

    return 1

# returns 1 if found title match, 2 if found title match and release date match, 0 o/w
def imdb_check_movie(movie, ia, date=None):
    movie = movie.lower()
    movie_results = ia.search_movie(movie)
    for index in range(min(len(movie_results), 2)):
        movie_match = movie_results[index]
        movie_title = movie_match.get('title').lower()

        if movie_title != movie:
            return 0

        release_date = imdb_check_movie_date(movie_match, date)
        if release_date != None and release_date == date - 1:
            return 2
    return 1

def imdb_check_movie_date(movie_match, date):
    if date == None: return None
    
    check_date = str(date - 1)
    ia.update(movie_match, info=['release dates'])
    movie_release_dates = movie_match.get('release dates')
    if movie_release_dates == None:
        return None

    for release in movie_release_dates:
        split_release = re.split('::|, | ', release)
        if check_date in split_release:
            return int(check_date)
    return None

def imdb_get_similar(entity, ia, year=None, type='movie'):
    entity = entity.lower()
    if type in ["movie", "tv series"]:
        entity_results = ia.search_movie(entity)
    else:
        entity_results = ia.search_person(entity)
    if not entity_results: return None
    found_result = entity_results[0]
    if _is_valid(found_result, year, type):
        return found_result.get('name').lower() if type == "person" else found_result.get('title').lower()
    return None

def _is_valid(result, year, type):
    if type in ["movie", "tv series"] and type != result.get('kind'): return False
    if result.get('year') is not None and str(int(result.get('year')) + 1) != year: return False
    return True

# will return most similar movie and entity
<<<<<<< HEAD
def imdb_get_similar_entity(entity, ia, year=None):
    similar = []
    for type in ["movie", "person", "tv series"]:
        similar.append(imdb_get_similar(entity, ia, year, type))
    return similar
=======
def imdb_get_similar_entity(entity, ia):
    return imdb_get_similar_movie(entity, ia), imdb_get_similar_entity(entity, ia)
>>>>>>> 99b4fec38e97813f9d4b944ff244eba56624c513

'''
print(imdb_check_entity('mel gibson', ia, 2014))
print(imdb_check_movie('Cheaper by the Dozen', ia, 2023))
print(imdb_check_person('mel gibson', ia, 2014))
print(imdb_check_person('Cheaper by the Dozen', ia, 2023))
print(ia.get_movie_infoset())
print(ia.get_person_infoset())
print(imdb_check_movie('Batman', ia, 2014))
'''
<<<<<<< HEAD
#print(imdb_get_similar_people('stallone', ia, 2013))
=======
#print(imdb_get_similar_people('stallone', ia, 2013))






>>>>>>> 99b4fec38e97813f9d4b944ff244eba56624c513

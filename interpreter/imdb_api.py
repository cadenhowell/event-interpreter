import imdb

# you will need to call 'var = imdb.IMDb() and pass var into get_imdb_check(entity, var) for it to have a db to reference
ia = imdb.IMDb()

def get_imdb_check(entity, ia):
    entity = entity.lower()
    movie_results = ia.search_movie(entity)
    for index in range(5):
        movie_match = movie_results[index]
        movie_title = movie_match.get('title').lower()
        if movie_title == entity:
            return 1

    person_results = ia.search_person(entity)
    for index in range(5):
        person_match = person_results[index]
        person_name = person_match.get('name').lower()
        if person_name == entity:
            return 1
    return 0

print(get_imdb_check('mel gibson'))




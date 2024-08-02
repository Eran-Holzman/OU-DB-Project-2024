from datetime import datetime

import psycopg2

from DB_handler import DB_handler

from SearchWizard import SearchWizard

from TextLoader import TextLoader

from TextBuilder import TextBuilder


def merge_dict_array(dict_array):
    merged_dict = {}
    for d in dict_array:
        for key, value in d.items():
            if key in merged_dict:
                merged_dict[key].extend(value)
            else:
                merged_dict[key] = value
    return merged_dict


dict_array = [
    {'When': [(1, 1, 1, ' ')]},
    {'he': [(1, 1, 2, ' ')]},
    {'was': [(1, 1, 3, ' ')]},
    {'a': [(1, 1, 4, ' '), (1, 1, 11, ' '), (1, 2, 3, ' '), (2, 1, 17, ' ')]},
    {'boy': [(1, 1, 5, ' ')]},
    {'growing': [(1, 1, 6, ' ')]},
    {'up': [(1, 1, 7, ' ')]},
    {'in': [(1, 1, 8, ' '), (1, 1, 13, ' '), (1, 1, 30, ' '), (1, 2, 11, ' '), (1, 5, 22, ' ')]},
    {'Wadi': [(1, 1, 9, ' '), (1, 5, 7, ' ')]},
    {'Musa': [(1, 1, 10, ', '), (1, 5, 8, ' ')]},
    {'town': [(1, 1, 12, ' ')]},
    {'southern': [(1, 1, 14, ' ')]},
    {'Jordan': [(1, 1, 15, ' '), (1, 2, 13, ', '), (2, 1, 83, ' ')]},
    {'Mohamad': [(1, 1, 16, ' ')]},
    {'Alfarajat': [(1, 1, 17, ' '), (1, 2, 1, ', '), (1, 3, 14, ' '), (1, 5, 13, '. "')]},
    {'says': [(1, 1, 18, ' '), (1, 2, 14, ' '), (1, 3, 15, '. "'), (1, 5, 12, ' ')]},
    {'his': [(1, 1, 19, ' '), (1, 2, 35, ' '), (2, 1, 200, ' ')]},
    {'father': [(1, 1, 20, ' '), (1, 2, 36, ' ')]},
    {'told': [(1, 1, 21, ' ')]},
    {'him': [(1, 1, 22, ' '), (1, 2, 40, '.\n')]},
    {'stories': [(1, 1, 23, ' ')]},
    {'of': [(1, 1, 24, ' '), (1, 2, 16, ' '), (1, 4, 35, ' '), (1, 4, 45, ' '), (1, 5, 3, ' '), (1, 5, 24, ' ')]},
    {'green': [(1, 1, 25, ' ')]},
    {'terraces': [(1, 1, 26, ' ')]},
    {'planted': [(1, 1, 27, ' ')]},
    {'with': [(1, 1, 28, ' '), (1, 1, 36, ' ')]},
    {'the': [(1, 1, 31, ' '), (1, 1, 45, ' '), (1, 2, 31, ' '), (1, 3, 8, ' '),
             (1, 4, 19, ' '), (1, 4, 33, ' '), (1, 4, 43, ' '), (1, 4, 46, ' '), (2, 2, 70, ' '), (2, 1, 324, ' ')]},
    {'region’s': [(1, 1, 32, ' ')]},
    {'desert': [(1, 1, 33, ' ')]},
    {'along': [(1, 1, 35, ' ')]},
    {'thriving': [(1, 1, 37, ' ')]},
    {'apricot': [(1, 1, 38, ' ')]},
    {'orchards': [(1, 1, 39, ' ')]},
    {'and': [(1, 1, 40, ' '), (1, 2, 21, ' '), (1, 2, 37, ' '), (1, 3, 28, ' '), (1, 4, 23, ' ')]},
    {'fig': [(1, 1, 41, ' ')]},
    {'trees': [(1, 1, 42, ' ')]},
    {'that': [(1, 1, 43, ' '), (1, 2, 17, ' '), (1, 2, 33, ' '), (1, 4, 39, ' ')]},
    {'fed': [(1, 1, 44, ' '), (1, 2, 34, ' ')]},
    {'local': [(1, 1, 46, ' '), (1, 4, 5, ' '), (1, 4, 24, ' ')]},
    {'community': [(1, 1, 47, '.\n'), (1, 3, 17, ' '), (2, 1, 328, ' '), (2, 2, 14, ' ')]},
    {'now': [(1, 2, 2, ' '), (1, 3, 29, ' ')]},
    {'geologist': [(1, 2, 4, ' '), (2, 1, 19, ' ')]},
    {'at': [(1, 2, 5, ' '), (1, 4, 42, ' '), (1, 5, 6, ' ')]},
    {'Al-Hussein': [(1, 2, 6, ' '), (2, 1, 32, ' ')]},
    {'Bin': [(1, 2, 7, ' '), (2, 1, 43, ' ')]},
    {'Talal': [(1, 2, 8, ' '), (2, 1, 47, ' ')]},
    {'University': [(1, 2, 9, ' '), (2, 1, 53, ' ')]},
    {'nearby': [(1, 2, 11, ' '), (2, 1, 68, ' ')]},
    {'Ma’an': [(1, 2, 12, ', '), (2, 1, 76, ', ')]},
    {'little': [(1, 2, 15, ' '), (2, 1, 95, ' ')]},
    {'bounty': [(1, 2, 18, ' '), (2, 1, 112, ' ')]},
    {'remains': [(1, 2, 19, '. '), (2, 1, 116, ' ')]},
    {'Longer': [(1, 2, 20, ' ')]},
    {'longer': [(1, 2, 22, ' ')]},
    {'dry': [(1, 2, 23, ' ')]},
    {'spells': [(1, 2, 24, ' ')]},
    {'have': [(1, 2, 25, ' '), (1, 4, 31, ' ')]},
    {'made': [(1, 2, 26, ' '), (1, 4, 4, ' '), (1, 4, 12, ' ')]},
    {'it': [(1, 2, 27, ' ')]},
    {'harder': [(1, 2, 28, ' ')]},
    {'to': [(1, 2, 29, ' '), (1, 3, 12, ' '), (1, 3, 19, ' '), (1, 5, 17, ' '), (1, 5, 28, ' ')]},
    {'maintain': [(1, 2, 30, ' ')]},
    {'fields': [(1, 2, 32, ' ')]},
    {'generations': [(1, 2, 38, ' ')]},
    {'before': [(1, 2, 39, ' ')]},
    {'"Since': [(1, 3, 1, ' ')]},
    {'climate': [(1, 3, 2, ' '), (1, 4, 8, ' '), (1, 5, 19, ' '), (1, 5, 4, ' ')]},
    {'change': [(1, 3, 3, ' '), (1, 4, 9, ' '), (1, 5, 5, ' '), (1, 5, 20, ' ')]},
    {'started': [(1, 3, 4, ' '), (1, 3, 11, ' ')]},
    {'40': [(1, 3, 5, ' ')]},
    {'years': [(1, 3, 6, ' '), (2, 2, 28, ' ')]},
    {'ago': [(1, 3, 7, ', ')]},
    {'fertile': [(1, 3, 9, ' ')]},
    {'areas': [(1, 3, 10, ' '), (2, 2, 53, ' ')]},
    {'contract': [(1, 3, 13, '," ')]},
    {'used': [(1, 3, 18, ' ')]},
    {'grow': [(1, 3, 20, ' ')]},
    {'its': [(1, 3, 21, ' '), (1, 3, 25, ' ')]},
    {'The': [(1, 3, 16, ' '), (1, 5, 1, ' ')]},
    {'own': [(1, 3, 22, ' '), (1, 3, 26, ' ')]},
    {'food': [(1, 3, 23, ' ')]},
    {'on': [(1, 3, 24, ' ')]},
    {'land': [(1, 3, 27, ', ')]},
    {'they': [(1, 3, 30, ' ')]},
    {'import': [(1, 3, 31, ' ')]},
    {'nearly': [(1, 3, 32, ' ')]},
    {'everything': [(1, 3, 33, ' ')]},
    {'from': [(1, 3, 34, ' ')]},
    {'outside': [(1, 3, 35, '."\n')]},
    {'As': [(1, 4, 1, ' ')]},
    {'drought': [(1, 4, 2, ' ')]},
    {'has': [(1, 4, 3, ' '), (1, 4, 10, ' ')]},
    {'agricultural': [(1, 4, 6, ' ')]},
    {'precarious': [(1, 4, 7, ', ')]},
    {'also': [(1, 4, 11, ' ')]},
    {'flash': [(1, 4, 13, ' ')]},
    {'flooding': [(1, 4, 14, ' ')]},
    {'more': [(1, 4, 15, ' '), (1, 4, 27, ' ')]},
    {'frequent': [(1, 4, 16, ', ')]},
    {'threatening': [(1, 4, 17, ' ')]},
    {'both': [(1, 4, 18, ' ')]},
    {"area's": [(1, 4, 20, ' ')]},
    {'ancient': [(1, 4, 21, ' ')]},
    {'ruins': [(1, 4, 22, ' ')]},
    {'communities': [(1, 4, 25, '. ')]},
    {'And': [(1, 4, 26, ' ')]},
    {'intense': [(1, 4, 28, ' ')]},
    {'temperature': [(1, 4, 29, ' ')]},
    {'swings': [(1, 4, 30, ' ')]},
    {'accelerated': [(1, 4, 32, ' ')]},
    {'weathering': [(1, 4, 34, ' ')]},
    {'historic': [(1, 4, 36, ' ')]},
    {'sandstone': [(1, 4, 37, ' ')]},
    {'facades': [(1, 4, 38, ' ')]},
    {'were': [(1, 4, 40, ' ')]},
    {'carved': [(1, 4, 41, ' ')]},
    {'height': [(1, 4, 44, ' ')]},
    {'Roman': [(1, 4, 47, ' ')]},
    {'Empire': [(1, 4, 48, '.\n')]},
    {'impact': [(1, 5, 2, ' ')]},
    {'is': [(1, 5, 9, ' ')]},
    {'very': [(1, 5, 10, ' ')]},
    {'clear': [(1, 5, 11, '," ')]},
    {'If': [(1, 5, 14, ' ')]},
    {'you': [(1, 5, 15, ' ')]},
    {'want': [(1, 5, 16, ' ')]},
    {'see': [(1, 5, 18, ' ')]},
    {'impacts': [(1, 5, 21, ' ')]},
    {'front': [(1, 5, 23, ' ')]},
    {'your': [(1, 5, 25, ' ')]},
    {'face': [(1, 5, 26, ', ')]},
    {'come': [(1, 5, 27, ' ')]},
    {'Petra': [(1, 5, 29, '."\n\n')]}
]

converted_dict = merge_dict_array(dict_array)

def convert_to_tuple(string_tuple, type_cast):
    # Remove the parentheses and split by commas
    items = string_tuple.strip('()').split(',')
    # Convert each item using the provided type_cast function
    return tuple(type_cast(item) for item in items)


# Connect to the database. PLEASE MAKE SURE TO change the  credentials to the ones on your local server.
connection = psycopg2.connect(dbname="db_project", user="omri", password="omri", options="-c search_path=text_handle")
cursor = connection.cursor()

db_test = DB_handler()

db_test.create_schemas()

db_test.create_types()

db_test.create_tables()

# db_test.create_triggers()

tl = TextLoader()

sw = SearchWizard()

tb = TextBuilder()

## Tests on Reporters table
##
reporter_id = tl.load_reporter('Yuval Levy')
cursor.execute(" SELECT * FROM art_info.reporters ")
print("Reporters table: ")
for row in cursor:
    print(row)
##
## End of tests on Reporters table

## Tests on Magazines table
##
np_id1 = tl.load_newspaper('The New York Times')
np_id2 = tl.load_newspaper('Washington Post')
cursor.execute("SELECT * FROM art_info.Newspapers")
print("Newspapers table: ")
for row in cursor:
    print(row)
cursor.close()
##
## End of tests on Magazines table
##
## Tests on Articles table
##
cursor = connection.cursor()
art_id1 = tl.load_article(np_id1, 'The Big Bang Theory', datetime(1987, 5, 30).date(), reporter_id)
art_id2 = tl.load_article(np_id2, 'friends', datetime(1987, 5, 30).date(), reporter_id)
cursor.execute("SELECT * FROM art_info.Articles ORDER BY article_id ")
print("Articles table: ")

for row in cursor:
    print(row)

cursor.close()

## Tests on words table
##

cursor = connection.cursor()

word_occurrence1 = []
word_occurrence3 = [{'Dog': [(1, 2, 3, ' '), (1, 3, 5, '?')]}]

tl.load_text(art_id1, converted_dict)
# tl.load_text(art_id2, word_occurrence1)
# tl.load_text(art_id2, word_occurrence3)

cursor.execute(" SELECT word_id, word, unnest(occurrences) FROM text_handle.words ")

# print("Words table: ")
# for row in cursor:
#     print(row)

# cursor.execute(" SELECT word_id, word, pos"
#                " from text_handle.words, unnest(occurrences) AS occ, unnest(occ.positions) AS pos;")
#
# print("Words table per position: ")
# for row in cursor:
#     print(row)
#     word = row[0]
#     position_str = row[1]
#     # Convert the string representations to actual tuples
cursor.close()


## Tests on SearchWizard

def extract_first_elements(tup_list):
    return [t[0] for t in tup_list]


article_list_test = sw.search_reporter_articles('yuval levy')
print("All article written Yuval Levy are: ")
print(article_list_test)

# article_list_test = sw.search_np_articles('The New York Times')
# print("article id of The New York Times is: ")
# print(extract_first_elements(article_list_test))
#
# article_list_test = sw.search_articles_date(datetime(1987, 5, 30).date())
# print("articles written on 1987-05-30 are: ")
# print(article_list_test)
#
# articles_word_test = sw.search_articles_word('Dog')
# print("articles according to word dog are: ")
# print(articles_word_test)
#
# #
# all_words = tb.all_words()
# print("All words in the database are: ")
# print(extract_first_elements(all_words))

# all_words_in_article = tb.all_words_in_article(art_id1[0])
# print("All words in article 1 are: ")
# print(extract_first_elements(all_words_in_article))

test_article = tb.build_entire_text('The Big Bang Theory')
# print("All words in article 1 are: ")
# print(extract_first_elements(all_words_in_article))

# context_arr = tb.build_context('The Big Bang Theory', 'Wadi')
# print("context_arr: ")
# for context in context_arr:
#     print("The context is: ")
#     print(context)

# indexes = tb.build_words_index('Alfarajat', 'The Big Bang Theory')
# print("The indexes are: ")
# print(indexes)


# word_at_position = sw.search_word_at_position('The Big Bang Theory', 4, 5, 12)
# print("The word at position is: ")
# print(word_at_position)

## End of tests on SearchWizard


cursor.close()
##
## End of tests on Reporters table
cursor = connection.cursor()

cursor.execute(" DROP TABLE art_info.Articles")
connection.commit()
connection.commit()
cursor.execute(" DROP TABLE art_info.newspapers")
connection.commit()
cursor.execute(" TRUNCATE TABLE art_info.reporters")
cursor.execute(" DROP TABLE art_info.reporters")
connection.commit()
cursor.execute(" DROP TABLE text_handle.word_groups ")
connection.commit()
cursor.execute(" DROP TABLE text_handle.words")
connection.commit()
# cursor.execute(" DROP TABLE text_handle.phrases")
# connection.commit()
cursor.execute(" drop type text_handle.occurrence_type; ")
cursor.execute(" drop type text_handle.position_type;")
connection.commit()
cursor.close()

# When he a growing up in a in

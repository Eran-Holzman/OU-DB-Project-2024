############################################################################################################
#              This module is responsible for loading text from the articles into the database             #
#              The functions in this class implement the 1st and 2nd requirements of the assignment        #
############################################################################################################

from DB_handler import DB_handler


def parse_name(full_name):
    # Split the full name by spaces
    parts = full_name.split()

    # Handle cases with no spaces (single name)
    if len(parts) == 1:
        return parts[0], ''

    # Handle cases with more than one space (more than two names)
    first_name = parts[0]
    last_name = ' '.join(parts[1:])

    return first_name, last_name


def convert_dict_to_array_of_tuples(big_dict):
    array_of_tuples = []
    for key, value in big_dict.items():
        array_of_tuples.append((key, value))
    return array_of_tuples


class TextLoader:
    def __init__(self):
        self.db_handler = DB_handler()

    def load_reporter(self, reporter_full_name):
        reporter_id = self.db_handler.get_reporter_id_from_name(reporter_full_name)
        # If the reporter is not in the database, we add him.
        if len(reporter_id) == 0:
            first_name = parse_name(reporter_full_name)[0]
            last_name = parse_name(reporter_full_name)[1]
            self.db_handler.cursor.execute(" INSERT INTO art_info.reporters (first_name, last_name) "
                                           " VALUES (%s, %s) RETURNING reporter_id", (first_name, last_name))
            self.db_handler.connection.commit()
            ret = self.db_handler.cursor.fetchall()[0][0]
        # If the reporter is in the database, we return the reporter_id.
        else:
            ret = reporter_id[0][0]
        return ret

    def load_newspaper(self, np_name):
        np_id = self.db_handler.get_np_id_from_name(np_name)
        # If the magazine is not in the database, we add it.
        if len(np_id) == 0:
            self.db_handler.cursor.execute(" INSERT INTO art_info.newspapers (np_id, np_name) "
                                           " VALUES (gen_random_uuid (), %s) RETURNING np_id", (np_name,))
            self.db_handler.connection.commit()
            ret = self.db_handler.cursor.fetchall()[0][0]
        else:
            ret = np_id[0][0]
        return ret

    def load_article(self, np_id, article_title, date, reporter_id):
        self.db_handler.cursor.execute(" INSERT INTO art_info.articles (np_id, article_title, date, reporter_id) "
                                       " VALUES (%s, %s, %s, %s) "
                                       " RETURNING article_id",
                                       (np_id, article_title, date, reporter_id))
        self.db_handler.connection.commit()
        article_id = self.db_handler.cursor.fetchall()
        return article_id

    #
    def load_text(self, article_id, dict_text):
        dis_text = convert_dict_to_array_of_tuples(dict_text)
        for word_occurrences in dis_text:
            self.db_handler.cursor.execute("SELECT word_id FROM text_handle.words WHERE word = %s",
                                           (word_occurrences[0],))
            self.db_handler.connection.commit()
            word_id = self.db_handler.cursor.fetchall()
            if len(word_id) == 0:
                self.db_handler.cursor.execute(" INSERT INTO text_handle.words (word, occurrences) VALUES ( "
                                               " %s,  ARRAY[ "
                                               "ROW( %s, %s::position_type[])]::occurrence_type[]) ",
                                               (word_occurrences[0], article_id[0][0], word_occurrences[1]))
                self.db_handler.connection.commit()
            # If the word is in the database, we add the new occurrences.
            else:
                new_positions_array = "ARRAY[%s]::position_type[]" % ','.join(
                    "ROW(%s, %s, %s, '%s', '%s')" % pos for pos in word_occurrences[1])
                # Create the new occurrence record
                new_occurrence_record = "ROW(%s, %s)::occurrence_type" % (article_id[0][0], new_positions_array)
                # Update the table to add the new occurrence
                self.db_handler.cursor.execute(
                    f"""
                    UPDATE text_handle.words 
                    SET occurrences = array_append(occurrences, {new_occurrence_record})
                    WHERE word_id = %s
                    """,
                    (word_id[0][0],)
                )
                self.db_handler.connection.commit()

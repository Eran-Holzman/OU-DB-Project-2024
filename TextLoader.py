"""
This module is responsible for loading text from articles into the database.
It implements the 1st and 2nd requirements of the assignment.

The module provides utility functions for name parsing and data conversion,
as well as a TextLoader class for handling database operations related to
reporters, newspapers, articles, and text content.
"""

from db_handler import *


def parse_name(full_name):
    """
    Parse a full name into first name and last name.

    Args:
        full_name (str): The full name to parse.

    Returns:
        Tuple[str, str]: A tuple containing the first name and last name.
    """
    parts = full_name.split()
    if len(parts) == 1:
        return parts[0], ''
    first_name = parts[0]
    last_name = ' '.join(parts[1:])
    return first_name, last_name


def convert_dict_to_array_of_tuples(big_dict):
    """
    Convert a dictionary to an array of tuples.

    Args:
        big_dict (Dict[str, Any]): The dictionary to convert.

    Returns:
        List[Tuple[str, Any]]: An array of tuples, where each tuple contains a key-value pair from the dictionary.
   """
    array_of_tuples = []
    for key, value in big_dict.items():
        array_of_tuples.append((key, value))
    return array_of_tuples


class TextLoader:
    """
    A class for loading text and related information into the database.

    This class provides methods for inserting and retrieving information about
    reporters, newspapers, articles, and text content.
    """

    def __init__(self):
        """Initialize the TextLoader with a database handler."""
        self.db_handler = DBHandler()

    def load_reporter(self, reporter_full_name):
        """
        Load a reporter into the database or retrieve their ID if already present.

        Args:
              reporter_full_name (str): The full name of the reporter.

        Returns:
             int: The reporter's ID in the database.
        """
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
        """
        Load a newspaper into the database or retrieve its ID if already present.

        Args:
            np_name (str): The name of the newspaper.

        Returns:
            str: The newspaper's ID (UUID) in the database.
       """
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
        """
        Load an article into the database.

        Args:
            np_id (str): The ID of the newspaper.
            article_title (str): The title of the article.
            date (str): The publication date of the article.
            reporter_id (int): The ID of the reporter who wrote the article.

        Returns:
            List[Tuple[int]]: A list containing a tuple with the article's ID.
        """
        self.db_handler.cursor.execute(" INSERT INTO art_info.articles (np_id, article_title, date, reporter_id) "
                                       " VALUES (%s, %s, %s, %s) "
                                       " RETURNING article_id",
                                       (np_id, article_title, date, reporter_id))
        self.db_handler.connection.commit()
        article_id = self.db_handler.cursor.fetchall()
        return article_id

    #
    def load_text(self, article_id, dict_text):
        """
        Load the text content of an article into the database.

        This method processes each word in the article, inserting new words into the database
        or updating existing words with new occurrences.

        Args:
            article_id (int): The ID of the article.
            dict_text (Dict[str, List[Tuple[int, int, int, str, str]]]): A dictionary where keys are words
                and values are lists of tuples representing the word's occurrences in the article.
                Each tuple contains (paragraph_number, line_number, position_in_line, starting_chars, finishing_chars).
        """
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
            else:
                new_positions_array = "ARRAY[%s]::position_type[]" % ','.join(
                    "ROW(%s, %s, %s, '%s', '%s')" % pos for pos in word_occurrences[1])
                new_occurrence_record = "ROW(%s, %s)::occurrence_type" % (article_id[0][0], new_positions_array)
                self.db_handler.cursor.execute(
                    f"""
                    UPDATE text_handle.words 
                    SET occurrences = array_append(occurrences, {new_occurrence_record})
                    WHERE word_id = %s
                    """,
                    (word_id[0][0],)
                )
                self.db_handler.connection.commit()

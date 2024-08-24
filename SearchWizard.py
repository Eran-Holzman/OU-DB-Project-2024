"""
This module is responsible for searches in the database according to key elements provided by the user.
It implements the 3rd requirement of the assignment.

The module provides utility functions for date parsing and tuple string parsing,
as well as a SearchWizard class for handling various article search operations.
"""

import streamlit as st
from db_handler import *
import pandas as pd
from datetime import *


def parse_date(date_str_inp):
    """
    Parse a date string into a datetime object.

    Args:
        date_str_inp (str): The date string to parse, expected format is 'Month day, Year'.

    Returns:
        Optional[datetime]: The parsed datetime object, or None if parsing fails.
       """
    try:
        ret = datetime.strptime(date_str_inp, '%B %d, %Y')
        return ret
    except ValueError:
        return None

class SearchWizard:
    """
    A class for performing various search operations on articles in the database.

    This class provides methods for searching articles by reporter, newspaper,
    date, and word, as well as handling the Streamlit UI for these search operations.
    """
    def __init__(self):
        """Initialize the SearchWizard with a database handler."""
        self.db_handler = DBHandler()

    ## The first 2 requirements are taken care of by the class db_handler

    ## The following cluster of functions is supposed to take care of requirement number 3
    #  in the project's requirements. The cluster ends in the next ##

    # Search for all the articles written by an reporter whose name was provided by the user.
    # The loop takes care of the case where there can be multiple reporters with the same name.
    # In that case, we fetch the articles that were written by all of them.
    def search_reporter_articles(self, reporter_full_name):
        """
        Search for all articles written by a reporter.

        Args:
            reporter_full_name (str): The full name of the reporter.

        Returns:
            Optional[List[Tuple[Any, ...]]]: A list of tuples containing article information,
            or None if no reporter name is provided.
        """
        if len(reporter_full_name) == 0:
            return None
        else:
            reporter_ids = self.db_handler.get_reporter_id_from_name(reporter_full_name)
            for reporter_id_tuple in reporter_ids:
                reporter_id = reporter_id_tuple[0]
                self.db_handler.cursor.execute(" SELECT a.article_title, n.np_name, a.date "
                                               " FROM art_info.articles a JOIN art_info.newspapers n "
                                               " ON a.np_id = n.np_id "
                                               " WHERE a.reporter_id = %s ", (reporter_id,))
                self.db_handler.connection.commit()
            return self.db_handler.cursor.fetchall()

    # Search for all the articles in a specific newspaper.
    # The assumption is that there are no 2 magazines with the same name.
    def search_np_articles(self, np_name):
        """
        Search for all articles in a specific newspaper.

        Args:
            np_name (str): The name of the newspaper.

        Returns:
            Optional[List[Tuple[Any, ...]]]: A list of tuples containing article information,
            or None if the newspaper is not found.
        """
        np_id_ret = self.db_handler.get_np_id_from_name(np_name)
        if len(np_id_ret) == 0:
            return None
        else:
            np_id = np_id_ret[0][0]
            self.db_handler.cursor.execute(" SELECT article_title, date "
                                           " FROM art_info.articles WHERE np_id = %s", (np_id,))
            self.db_handler.connection.commit()
            return self.db_handler.cursor.fetchall()

    # Search for all the articles that were published a specific date
    def search_articles_date(self, date):
        """
        Search for all articles published on a specific date.

        Args:
            date (datetime): The date to search for.

        Returns:
            List[Tuple[Any, ...]]: A list of tuples containing article information.
        """
        self.db_handler.cursor.execute(" SELECT a.article_title, n.np_name "
                                       " FROM art_info.articles a JOIN art_info.newspapers n "
                                       " ON a.np_id = n.np_id "
                                       " WHERE a.date = %s", (date,))
        self.db_handler.connection.commit()
        return self.db_handler.cursor.fetchall()

    # Search for all the articles that contain a specific word.
    def search_articles_word(self, word):
        """
        Search for all articles containing a specific word.

        Args:
            word (str): The word to search for.

        Returns:
            Optional[List[Tuple[Any, ...]]]: A list of tuples containing article information,
            or None if no word is provided.
        """
        if len(word) == 0:
            return None
        else:
            word_id = self.db_handler.get_word_id_from_word(word)
            self.db_handler.cursor.execute(" SELECT a.article_title, n.np_name, a.date "
                                           " FROM art_info.articles a JOIN art_info.newspapers n "
                                           " ON a.np_id = n.np_id "
                                           " WHERE a.article_id IN"
                                           " (SELECT (unnest(occurrences)).article_id AS article_id "
                                           " FROM text_handle.words "
                                           " WHERE word_id = %s)", (word_id,))
            self.db_handler.connection.commit()
            return self.db_handler.cursor.fetchall()

    def search_word_at_position(self, article_title, paragraph_number, line_number, position_in_line):
        """
        Search for a word at a specific position in an article.

        Args:
            article_title (str): The title of the article.
            paragraph_number (int): The paragraph number.
            line_number (int): The line number.
            position_in_line (int): The position in the line.

        Returns:
            Optional[str]: The word at the specified position, or None if not found.
        """
        article_id = self.db_handler.get_article_id_from_title(article_title)[0][0]
        query = """
            SELECT word
            FROM words,
                 LATERAL unnest(occurrences) AS occ(article_id, positions),
                 LATERAL unnest(occ.positions) AS pos(paragraph_number, line_number, position_in_line, finishing_chars)
            WHERE occ.article_id = %s
              AND pos.paragraph_number = %s
              AND pos.line_number = %s
              AND pos.position_in_line = %s;
        """
        self.db_handler.cursor.execute(query, (article_id, paragraph_number, line_number, position_in_line))
        self.db_handler.connection.commit()
        res = self.db_handler.cursor.fetchone()
        if res:
            return res[0]
        else:
            return None


    ## End of the cluster of functions for requirement number 3

    ## The following cluster of functions is supposed to take care of requirement number 4
    #  in the project's requirements. The cluster ends in the next ##
    # def
    ## End of the cluster of functions for requirement number 4
    def handle_search_reporter_articles(self):
        """Handle the Streamlit UI for searching articles by reporter."""
        reporter_name = st.text_input("Please enter a reporter's name: ")
        articles_of_reporter = self.search_reporter_articles(reporter_name)
        if articles_of_reporter is not None and len(articles_of_reporter) != 0:
            df = pd.DataFrame(articles_of_reporter, columns=["Article Title", "Newspaper", "Date"])
            st.subheader(f"Articles written by {reporter_name}: ")
            st.dataframe(df, hide_index=True)
        elif articles_of_reporter is not None and len(articles_of_reporter) == 0:
            st.error("No articles found.")

    def handle_search_newspaper_articles(self):
        """Handle the Streamlit UI for searching articles by newspaper."""
        newspaper_name = st.text_input("Please enter a newspaper's name: ")
        articles_of_newspaper = self.search_np_articles(newspaper_name)
        if articles_of_newspaper is not None and len(articles_of_newspaper) != 0:
            df = pd.DataFrame(articles_of_newspaper, columns=["Article Title", "Date"])
            st.subheader(f"Articles in {newspaper_name}: ")
            st.dataframe(df, hide_index=True)
        elif articles_of_newspaper is not None and len(articles_of_newspaper) == 0:
            st.error("No articles found.")
        elif articles_of_newspaper is None and len(newspaper_name) != 0:
            st.error("Invalid newspaper")

    def handle_search_date_articles(self):
        """Handle the Streamlit UI for searching articles by date."""
        date_str = st.text_input("Please enter a date (e.g. January 1, 2022): ")
        if len(date_str) != 0:
            p_date = parse_date(date_str)
            if p_date is not None:
                articles_of_date = self.search_articles_date(p_date)
                if articles_of_date is not None and len(articles_of_date) != 0:
                    df = pd.DataFrame(articles_of_date, columns=["Article Title", "Newspaper"])
                    st.subheader(f"Articles published on {date_str}: ")
                    st.dataframe(df, hide_index=True)
                elif articles_of_date is not None and len(articles_of_date) == 0:
                    st.error("No articles found.")
            else:
                st.write("Invalid date format. Please enter a date in the format 'Month day, year'.")

    def handle_search_word_articles(self):
        """Handle the Streamlit UI for searching articles by word."""
        word = st.text_input("Please enter a word: ")
        articles_of_word = self.search_articles_word(word)
        if articles_of_word is not None and len(articles_of_word) != 0:
            df = pd.DataFrame(articles_of_word, columns=["Article Title", "Newspaper", "Date"])
            st.subheader(f"Articles containing the word '{word}': ")
            st.dataframe(df, hide_index=True)
        elif articles_of_word is not None and len(articles_of_word) == 0:
            st.error("No articles found.")

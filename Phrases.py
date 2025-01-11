"""
This module handles phrase-related operations for the article processing system.
It provides functionality for defining, searching, and managing phrases within articles.
"""

import re

import pandas as pd
from text_highlighter import text_highlighter
from annotated_text import annotated_text
from db_handler import *
from text_builder import TextBuilder
import streamlit as st


def search_phrase_in_text(phrase, text):
    """
    Search for occurrences of a phrase in a given text.

    Args:
        phrase (str): The phrase to search for.
        text (str): The text to search in.

    Returns:
        list: A list of tuples containing the start and end positions of each occurrence.
    """
    matches = re.finditer(re.escape(phrase), text)
    res = []
    for match in matches:
        start = match.start()
        end = match.end()
        res.append((start, end))
    return res


class Phrases:
    """
    Handles phrase-related operations including definition, searching, and UI interactions.

    This class provides methods for defining new phrases, searching for phrases in articles,
    and managing the UI for phrase-related operations.
    """
    def __init__(self):
        """Initialize the Phrases class with database handler and text builder."""
        self.db_handler = DBHandler()
        self.tb = TextBuilder()

    def define_phrase(self, phrase):
        """
        Define a new phrase in the database.

        Args:
           phrase (str): The phrase to be defined.
        """
        self.db_handler.cursor.execute(" INSERT INTO text_handle.phrases (phrase) VALUES (%s) ", (phrase,))
        self.db_handler.connection.commit()

    def get_all_phrases(self):
        """
        Retrieve all defined phrases from the database.

        Returns:
            list: A list of tuples containing all defined phrases.
        """
        self.db_handler.cursor.execute(" SELECT phrase FROM text_handle.phrases ")
        self.db_handler.connection.commit()
        phrases = self.db_handler.cursor.fetchall()
        return phrases

    def is_phrase_defined(self, phrase):
        """
        Check if a phrase is already defined in the database.

        Args:
            phrase (str): The phrase to check.

        Returns:
            bool: True if the phrase is defined, False otherwise.
        """
        phrases = self.get_all_phrases()
        for ph in phrases:
            if phrase == ph[0]:
                return True

    def create_phrase_list(self):
        """
        Create a numbered list of all defined phrases.

        Returns:
            list: A list of tuples containing phrase numbers and phrases.
        """
        phrases_tup_arr = self.get_all_phrases()
        ret = []
        i = 0
        for phrase_tup in phrases_tup_arr:
            i += 1
            ret.append((i, phrase_tup[0]))
        return ret

    def manual_phrase_definition(self):
        """
        Handle the UI for manual phrase definition.

        This method allows users to define new phrases and view existing ones.
        """
        phrase = st.text_input("Enter phrase")
        if st.button("Save phrase"):
            if phrase:
                try:
                    self.define_phrase(phrase)
                    st.success(f"Phrase '{phrase}' defined successfully.")
                    st.subheader("My phrases: ")
                    df = pd.DataFrame(self.create_phrase_list(), columns=["", "phrase"])
                    st.dataframe(df, hide_index=True)
                except Exception as e:
                    st.error("""Error while defining the phrase. One of the following could be the reason:  \n
1. The phrase is already defined.  \n
2. The phrase has non-ascii characters.  \n
3. The phrase is longer than 100 characters.""")
            if st.button("Start a new manual phrase definition"):
                self.manual_phrase_definition()

    def phrases_in_text(self):
        """
        Handle the UI for searching phrases in an article.

        This method allows users to select an article, highlight phrases,
        and search for their occurrences in the article.
        """
        article_title = st.selectbox("Please select an article", self.tb.create_article_titles_array())
        if article_title and article_title != "Please select":
            st.divider()
            annotated_text(
                ("To search a phrase in the text, highlight it and click the 'Search' button at "
                 "the bottom of the page.", "", "yellow"),
            )
            st.divider()
            annotated_text(
                ("Please note, the phrase you're searching for will be saved in "
                 " 'my phrases' automatically", "", "yellow"),
            )
            st.divider()
            article = self.tb.build_entire_text(article_title)
            st.write(f"Title: {article[0]}")
            st.write(f"Date: {article[1]}")
            st.write(f"Reporter: {article[2]}")
            st.write("Content:")
            result = text_highlighter(
                text=article[3].replace('\n', '  \n'),
                labels=[("define", "yellow"), ("search", "blue")],
                annotations=[],
            )
            if st.button("Search"):
                for annotation in result:
                    try:
                        if not self.is_phrase_defined(annotation['text']):
                            self.define_phrase(annotation['text'])
                    except Exception as e:
                        st.error("Error while defining the phrase. It is possible that it is already defined")
                try:
                    for annotation in result:
                        res = [annotation]
                        for appearance in search_phrase_in_text(annotation['text'], article[3].replace('\n', '  \n')):
                            start, end = appearance
                            if start != annotation["start"] and end != annotation["end"]:
                                new_annotation = {'start': start, 'end': end, 'text': annotation['text'],
                                                  'tag': 'search', 'color': 'blue'}
                                result.append(new_annotation)
                                res.append(new_annotation)
                        result2 = text_highlighter(
                            text=article[3].replace('\n', '  \n'),
                            labels=[("define", "yellow"), ("search", "blue")],                            annotations=res,
                        )
                        break
                    if st.button("Start a new search in article"):
                        self.phrases_in_text()
                except Exception as e:
                    st.error("Error while searching the phrase.")

    def manual_phrase_search(self):
        """
        Handle the UI for manual phrase searching in an article.

        This method allows users to select an article, choose a predefined phrase,
        and search for its occurrences in the article.
        """
        article_title = st.selectbox("Please select an article to search the phrase in",
                                     self.tb.create_article_titles_array())
        if article_title and article_title != "Please select":
            st.subheader("My phrases: ")
            df = pd.DataFrame(self.create_phrase_list(), columns=["", "phrase"])
            st.dataframe(df, hide_index=True)
            phrase = st.text_input("Enter phrase")
            if st.button("Search"):
                if phrase:
                    if not self.is_phrase_defined(phrase):
                        st.error("Error: Phrase not defined")
                    else:
                        article = self.tb.build_entire_text(article_title)
                        result = []
                        for appearance in search_phrase_in_text(phrase, article[3].replace('\n', '  \n')):
                            start, end = appearance
                            new_annotation = {'start': start, 'end': end, 'text': phrase,
                                              'tag': 'searched word', 'color': 'blue'}
                            result.append(new_annotation)
                        if not result:
                            annotated_text(
                                ("Phrase not found in the article", "", "red"),
                            )
                        st.write(f"Title: {article[0]}")
                        st.write(f"Date: {article[1]}")
                        st.write(f"Reporter: {article[2]}")
                        st.write("Content:")
                        result2 = text_highlighter(
                            text=article[3].replace('\n', '  \n'),
                            labels=[("searched word", "blue")],
                            annotations=result,
                        )
                        if st.button("Start a new search in article"):
                            self.manual_phrase_search()


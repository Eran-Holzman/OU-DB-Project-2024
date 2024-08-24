"""
This module handles text manipulation, file uploading, and breaking down words for article processing.
It contains utility functions and the Article class for managing article content.
"""
import re
from text_loader import *
from typing import Dict, List, Tuple


def split_word(word):
    """
    Split a word into its alphabetic part and surrounding non-alphabetic characters.

    Args:
        word (str): The word to split.

    Returns:
        Tuple[str, str, str]: A tuple containing:
            - Beginning non-alphabetic characters
            - The alphabetic part of the word
            - Ending non-alphabetic characters
    """
    index1 = 0
    beg_chars = ''
    while index1 < len(word) and not word[index1].isalnum():
        if index1 < len(word):
            beg_chars += word[index1]
        index1 += 1
    end_chars_rev = ''
    index2 = len(word) - 1
    while index2 >= 0 and not word[index2].isalnum():
        if index2 >= 0:
            end_chars_rev += word[index2]
        index2 -= 1
    end_chars = ''
    for char in reversed(end_chars_rev):
        end_chars += char
    return beg_chars, word[index1:index2 + 1], end_chars



def is_only_none_alnum(word):
    """
   Check if a word contains only non-alphanumeric characters.

   Args:
       word (str): The word to check.

   Returns:
       bool: True if the word contains only non-alphanumeric characters, False otherwise.
   """
    for char in word:
        if char.isalnum():
            return False
    return True


class Article:
    """
   Represents an article with its content and metadata.

   This class handles the processing of article text, breaking it down into words
   and their positions, and interacts with the database for storage and retrieval.

   Attributes:
       title (str): The title of the article.
       authors (str): The author(s) of the article.
       newspaper (str): The name of the newspaper the article is from.
       date (str): The publication date of the article.
       content (str): The full text content of the article.
       words (Dict[str, List[Tuple[int, int, int, str, str]]]): A dictionary mapping words to their positions and surrounding punctuation.
       tl (text_loader): An instance of TextLoader for database interactions.
       """

    def __init__(self, txt_file):
        """
       Initialize an Article object from a text file.

       Args:
           txt_file (str): The content of the text file containing the article.
        """
        lines = txt_file.split('\n')
        self.title = lines[0].strip()
        self.authors = lines[1].strip()
        self.newspaper = lines[2].strip()
        self.date = lines[3].strip()
        self.content = '\n'.join(lines[4:]).strip()
        self.words: Dict[str, List[Tuple[int, int, int, str, str]]] = {}
        self.tl = TextLoader()

    def process_content(self):
        """
        Process the article content, breaking it down into words and their positions.

        This method splits the content into paragraphs, lines, and words, recording the
        position of each word along with its surrounding punctuation. It then loads this
        information into the database using the TextLoader.
        """
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', self.content) if p.strip()]
        for p_index, paragraph in enumerate(paragraphs, start=1):
            lines = paragraph.split('\n')
            for l_index, line in enumerate(lines, start=1):
                is_last_line_in_paragraph = (l_index == len(lines))
                words_in_line = line.split()
                word_position = 0
                for w_index, word in enumerate(words_in_line, start=1):
                    if not is_only_none_alnum(word):
                        word_tuple = split_word(word)
                    else:
                        word_tuple = ('', word, '')
                    is_last_word_in_line = (w_index == len(words_in_line))
                    word_position += 1
                    if is_last_line_in_paragraph and is_last_word_in_line:
                        tup = (p_index, l_index, word_position, word_tuple[0], word_tuple[2] + '\n\n')
                    elif is_last_word_in_line:
                        tup = (p_index, l_index, word_position, word_tuple[0], word_tuple[2] + '\n')
                    else:
                        tup = (p_index, l_index, word_position, word_tuple[0], word_tuple[2])
                    if word_tuple[1] not in self.words:
                        self.words[word_tuple[1]] = []
                    self.words[word_tuple[1]].append(tup)
        reporter_id = self.tl.load_reporter(self.authors)
        np_id = self.tl.load_newspaper(self.newspaper)
        article_id = self.tl.load_article(np_id, self.title, self.date, reporter_id)
        self.tl.load_text(article_id, self.words)

    def get_title(self):
        """
        Get the article title.

        Returns:
            str: The title of the article.
        """
        return self.title

    def get_authors(self):
        """
        Get the article authors.

        Returns:
            str: The author(s) of the article.
        """
        return self.authors

    def get_newspaper(self) -> str:
        """
        Get the newspaper name.

        Returns:
            str: The name of the newspaper.
        """
        return self.newspaper

    def get_date(self) -> str:
        """
        Get the publication date.

        Returns:
            str: The publication date of the article.
        """
        return self.date

    def get_content(self) -> str:
        """
        Get the full content of the article.

        Returns:
            str: The full text content of the article.
        """
        return self.content






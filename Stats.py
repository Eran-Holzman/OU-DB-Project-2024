"""
This module is responsible for calculating db statistics
The methods in this class implement the last requirements in the assignment
"""
from db_handler import *


class Stats:
    def __init__(self):
        """
        Initializes the Stats class with a DB_handler instance.
        """
        self.db_handler = DBHandler()

    def num_of_chars_per_word(self):
        """
        Returns a table with the word and the length of each word in the database.

        Returns:
            List[Tuple[str, int]]: A list of tuples, each containing a word and its length.
        """
        self.db_handler.cursor.execute("""SELECT word, char_length(word) as word_length 
                                          FROM text_handle.words
                                          ORDER BY word_length""")
        self.db_handler.connection.commit()
        return self.db_handler.cursor.fetchall()

    def avg_num_of_chars_per_word(self):
        """
        Calculates the average number of characters per word in the database.

        Returns:
            float: The average number of characters per word.
        """
        self.db_handler.cursor.execute("SELECT ROUND(AVG(char_length(word)),2) "
                                       "FROM text_handle.words")
        self.db_handler.connection.commit()
        return self.db_handler.cursor.fetchall()[0][0]

    def num_of_chars_per_word_in_article(self, article_title):
        """
        Returns a table with the word and the length of each word in a specific article.

        Args:
            article_title (str): The title of the article.

        Returns:
            List[Tuple[str, int]]: A list of tuples, each containing a word and its length in the specified article.
        """
        article_id_full = self.db_handler.get_article_id_from_title(article_title)
        if article_id_full:
            article_id = article_id_full[0][0]
            self.db_handler.cursor.execute("""
                                            SELECT 
                                                w.word, 
                                                char_length(w.word) as word_length
                                            FROM 
                                                text_handle.words w,
                                                unnest(w.occurrences) as o(article_id, positions)
                                            WHERE 
                                                o.article_id = %s  
                                            """, (article_id,))
            self.db_handler.connection.commit()
            return self.db_handler.cursor.fetchall()

    def avg_num_of_chars_per_word_in_article(self, article_title):
        """
        Calculates the average number of characters per word in a specific article.

        Args:
            article_title (str): The title of the article.

        Returns:
            float: The average number of characters per word in the article.
        """
        article_id_full = self.db_handler.get_article_id_from_title(article_title)
        if article_id_full:
            article_id = article_id_full[0][0]
            self.db_handler.cursor.execute("""
                                            SELECT ROUND(AVG(char_length(w.word)),2)
                                            FROM 
                                                text_handle.words w,
                                                unnest(w.occurrences) as o(article_id, positions)
                                            WHERE 
                                                o.article_id = %s  
                                            """, (article_id,))
            self.db_handler.connection.commit()
            return self.db_handler.cursor.fetchall()[0][0]

    def num_of_characters_in_line(self, article_title):
        """
        Calculates the total number of characters for each line in a specific article, including spaces.

        Args:
            article_title (str): The title of the article.

        Returns:
            List[Tuple[int, int, int]]: A list of tuples, each containing (paragraph_number, line_number, total_characters_in_line).
        """
        article_id_full = self.db_handler.get_article_id_from_title(article_title)
        if article_id_full:
            article_id = article_id_full[0][0]
            self.db_handler.cursor.execute("""
                                            SELECT 
                                                paragraph_number,
                                                line_number,
                                                SUM(char_length(word)) + SUM(char_length(starting_chars)) +SUM(char_length(finishing_chars)) + 
                                                MAX(position_in_line) -2 AS total_characters_in_line
                                            FROM 
                                                text_handle.words_positions
                                            WHERE article_id = %s
                                            GROUP BY 
                                                paragraph_number, line_number
                                            ORDER BY        
                                                paragraph_number, line_number
                                            """, (article_id,))
            self.db_handler.connection.commit()
            return self.db_handler.cursor.fetchall()

    def avg_of_characters_in_line(self, article_title):
        """
        Calculates the average number of characters per line in a specific article.

        Args:
            article_title (str): The title of the article.

        Returns:
            float: The average number of characters per line.
        """
        article_id_full = self.db_handler.get_article_id_from_title(article_title)
        if article_id_full:
            article_id = article_id_full[0][0]
            self.db_handler.cursor.execute("""
                                            SELECT ROUND(AVG(total_characters_in_line),2) AS avg_chars_in_line
                                            FROM (SELECT 
                                                        paragraph_number,
                                                        line_number,
                                                        SUM(char_length(word)) + SUM(char_length(starting_chars)) +SUM(char_length(finishing_chars)) + 
                                                        MAX(position_in_line) -2 AS total_characters_in_line
                                                    FROM 
                                                        text_handle.words_positions
                                                    WHERE article_id = %s
                                                    GROUP BY 
                                                        paragraph_number, line_number) AS chars_in_line
                                            """, (article_id,))
            self.db_handler.connection.commit()
            return self.db_handler.cursor.fetchall()[0][0]

    def num_of_chars_in_paragraph(self, article_title):
        """
        Calculates the total number of characters in each paragraph of a specific article.

        Args:
            article_title (str): The title of the article.

        Returns:
            List[Tuple[int, int]]: A list of tuples, each containing (paragraph_number, total_characters_in_paragraph).
        """
        article_id_full = self.db_handler.get_article_id_from_title(article_title)
        if article_id_full:
            article_id = article_id_full[0][0]
            self.db_handler.cursor.execute("""
                                            SELECT 
                                                paragraph_number,
                                                SUM(char_length(word)) + SUM(char_length(starting_chars)) + SUM(char_length(finishing_chars)) + 
                                                COUNT(word) - (COUNT(DISTINCT line_number) + 2) AS total_characters_in_paragraph
                                            FROM 
                                                text_handle.words_positions
                                            WHERE article_id = %s
                                            GROUP BY 
                                                paragraph_number
                                            """, (article_id,))
            self.db_handler.connection.commit()
            return self.db_handler.cursor.fetchall()

    def avg_chars_in_paragraph(self, article_title):
        """
        Calculates the average number of characters per paragraph in a specific article.

        Args:
            article_title (str): The title of the article.

        Returns:
            float: The average number of characters per paragraph.
        """
        article_id_full = self.db_handler.get_article_id_from_title(article_title)
        if article_id_full:
            article_id = article_id_full[0][0]
            self.db_handler.cursor.execute("""
                                            SELECT ROUND(AVG(total_characters_in_paragraph),2) AS avg_char_in_paragraph
                                            FROM(  SELECT 
                                                        paragraph_number,
                                                        SUM(char_length(word)) + SUM(char_length(starting_chars)) + SUM(char_length(finishing_chars)) + 
                                                        COUNT(word) - (COUNT(DISTINCT line_number) + 2)
                                                     AS total_characters_in_paragraph
                                                    FROM 
                                                        text_handle.words_positions
                                                    WHERE article_id = %s
                                                    GROUP BY 
                                                        paragraph_number) AS total_chars_per_paragraph
                                            """, (article_id,))
            self.db_handler.connection.commit()
            return self.db_handler.cursor.fetchall()[0][0]

    def num_of_chars_in_article(self, article_title):
        """
        Calculates the total number of characters in a specific article.

        Args:
            article_title (str): The title of the article.

        Returns:
            int: The total number of characters in the article.
        """
        article_id_full = self.db_handler.get_article_id_from_title(article_title)
        if article_id_full:
            article_id = article_id_full[0][0]
            self.db_handler.cursor.execute("""
                                            SELECT SUM(total_characters_in_paragraph) + 
                                                   (count(*)-1)*2 AS total_chars_in_Article
                                            FROM(SELECT SUM(char_length(word)) + SUM(char_length(starting_chars)) + 
                                                        SUM(char_length(finishing_chars)) + COUNT(word) - 
                                                        (COUNT(DISTINCT line_number) + 2) AS total_characters_in_paragraph
                                                    FROM 
                                                        text_handle.words_positions
                                                    WHERE article_id = %s
                                                    GROUP BY paragraph_number) AS total_chars_per_paragraph
                                                                                        """, (article_id,))
            self.db_handler.connection.commit()
            return self.db_handler.cursor.fetchall()[0][0]

    def num_of_chars_in_db(self):
        """
        Calculates the total number of characters in the entire database (all articles).

        Returns:
            List[Tuple[int]]: A list containing a single tuple with the total character count.
        """
        self.db_handler.cursor.execute("""
                                        SELECT SUM(total_chhars_per_article)
                                        FROM(
                                        SELECT SUM(total_characters_in_paragraph) + (MAX(total_paragraphs)-1) *
                                         2 AS total_chhars_per_article
                                        FROM(
                                            SELECT article_id, SUM(char_length(word)) + 
                                            SUM(char_length(starting_chars)) + SUM(char_length(finishing_chars)) + 
                                            COUNT(word) - (COUNT(DISTINCT line_number) + 2) AS total_characters_in_paragraph, 
                                            COUNT(paragraph_number) over (partition by article_id) as total_paragraphs
                                            FROM 
                                                text_handle.words_positions
                                            GROUP BY article_id, paragraph_number) AS total_in_Article
                                        GROUP BY article_id
                                        )""")
        self.db_handler.connection.commit()
        return self.db_handler.cursor.fetchall()

    # Returns the number of characters in the entire database(Of all the articles)
    def avg_chars_in_db(self):
        """
        Calculates the average number of characters per article in the entire database.

        Returns:
            float: The average number of characters per article.
        """
        self.db_handler.cursor.execute("""
                                        SELECT ROUND(AVG(total_chhars_per_article),2)
                                        FROM(
                                        SELECT SUM(total_characters_in_paragraph) + (MAX(total_paragraphs)-1) 
                                        * 2 AS total_chhars_per_article
                                        FROM(
                                            SELECT article_id, SUM(char_length(word)) + 
                                                               SUM(char_length(starting_chars)) + 
                                                               SUM(char_length(finishing_chars)) + 
                                                               COUNT(word) - (COUNT(DISTINCT line_number) + 2) 
                                                               AS total_characters_in_paragraph, 
                                                               COUNT(paragraph_number) over 
                                                               (partition by article_id) as total_paragraphs
                                                    FROM 
                                                        text_handle.words_positions
                                                    GROUP BY article_id, paragraph_number) AS total_in_Article
                                        GROUP BY article_id)""")
        self.db_handler.connection.commit()
        return self.db_handler.cursor.fetchall()

    def num_of_words_in_db(self):
        """
        Counts the total number of unique words in the database.

        Returns:
            List[Tuple[int]]: A list containing a single tuple with the total word count.
        """
        self.db_handler.cursor.execute("""SELECT COUNT(word_id)
                                          FROM text_handle.words""")
        self.db_handler.connection.commit()
        return self.db_handler.cursor.fetchall()

    def num_of_words_in_article(self, article_title):
        """
        Counts the total number of words in a specific article.

        Args:
            article_title (str): The title of the article.

        Returns:
            List[Tuple[int]]: A list containing a single tuple with the word count for the article.
        """
        article_id_full = self.db_handler.get_article_id_from_title(article_title)
        if article_id_full:
            article_id = article_id_full[0][0]
            self.db_handler.cursor.execute("""SELECT COUNT(word)
                                              FROM text_handle.words_positions
                                              WHERE article_id = %s""", (article_id,))
            self.db_handler.connection.commit()
            return self.db_handler.cursor.fetchall()

    def num_of_words_in_paragraph(self, article_title):
        """
        Counts the number of words in each paragraph of a specific article.

        Args:
            article_title (str): The title of the article.

        Returns:
            List[Tuple[int]]: A list of tuples, each containing the word count for a paragraph.
        """
        article_id_full = self.db_handler.get_article_id_from_title(article_title)
        if article_id_full:
            article_id = article_id_full[0][0]
            self.db_handler.cursor.execute("""  SELECT COUNT(word)
                                                FROM text_handle.words_positions
                                                WHERE article_id = %s
                                                GROUP BY paragraph_number
                                                ORDER BY paragraph_number""", (article_id,))
            self.db_handler.connection.commit()
            return self.db_handler.cursor.fetchall()

    def avg_words_in_paragraph(self, article_title):
        """
        Calculates the average number of words per paragraph in a specific article.

        Args:
            article_title (str): The title of the article.

        Returns:
            List[Tuple[float]]: A list containing a single tuple with the average word count per paragraph.
        """
        article_id_full = self.db_handler.get_article_id_from_title(article_title)
        if article_id_full:
            article_id = article_id_full[0][0]
            self.db_handler.cursor.execute("""  SELECT ROUND(AVG(num_of_words_per_par), 2)
                                                FROM (SELECT COUNT(word) AS num_of_words_per_par
                                                FROM text_handle.words_positions
                                                WHERE article_id = %s
                                                GROUP BY paragraph_number)""", (article_id,))
            self.db_handler.connection.commit()
            return self.db_handler.cursor.fetchall()

    def num_of_words_in_line(self, article_title):
        """
        Counts the number of words in each line of a specific article.

        Args:
            article_title (str): The title of the article.

        Returns:
            List[Tuple[int, int, int]]: A list of tuples, each containing (paragraph_number, line_number, num_of_words_in_line).
        """
        article_id_full = self.db_handler.get_article_id_from_title(article_title)
        if article_id_full:
            article_id = article_id_full[0][0]
            self.db_handler.cursor.execute("""  SELECT paragraph_number, line_number, COUNT(word) AS num_of_words_in_line
                                                FROM text_handle.words_positions
                                                WHERE article_id = %s
                                                GROUP BY paragraph_number, line_number
                                                ORDER BY paragraph_number, line_number""", (article_id,))
            self.db_handler.connection.commit()
            return self.db_handler.cursor.fetchall()

    # Returns the average number of words in the line
    def avg_words_in_line(self, article_title):
        """
        Calculates the average number of words per line in a specific article.

        Args:
            article_title (str): The title of the article.

        Returns:
            List[Tuple[float]]: A list containing a single tuple with the average word count per line.
        """
        article_id_full = self.db_handler.get_article_id_from_title(article_title)
        if article_id_full:
            article_id = article_id_full[0][0]
            self.db_handler.cursor.execute("""  SELECT ROUND(AVG(num_of_words_in_line), 2) as avg_words_per_line
                                                FROM(   SELECT paragraph_number, line_number, 
                                                        COUNT(word) AS num_of_words_in_line
                                                        FROM text_handle.words_positions
                                                        WHERE article_id = %s
                                                        GROUP BY paragraph_number, line_number) AS num_words_per_line""",
                                           (article_id,))
            self.db_handler.connection.commit()
            return self.db_handler.cursor.fetchall()

    def frequency_list_db(self):
        """
        Generates a frequency list of words for the entire database.

        Returns:
            List[Tuple[int, str, int]]: A list of tuples, each containing (row_number, word, frequency) for all words in the database.
        """
        self.db_handler.cursor.execute("""  SELECT ROW_NUMBER() OVER 
                                            (ORDER BY word) AS row_number, word, COUNT(word) AS frequency 
                                            FROM text_handle.words_positions
                                            GROUP BY word""")
        self.db_handler.connection.commit()
        return self.db_handler.cursor.fetchall()

    def frequency_list_article(self, article_title):
        """
        Generates a frequency list of words for a specific article.

        Args:
            article_title (str): The title of the article.

        Returns:
            List[Tuple[int, str, int]]: A list of tuples, each containing (row_number, word, frequency) for all words in the specified article.
        """
        article_id_full = self.db_handler.get_article_id_from_title(article_title)
        if article_id_full:
            article_id = article_id_full[0][0]
            self.db_handler.cursor.execute("""  SELECT ROW_NUMBER() OVER (ORDER BY word) AS row_number, word, 
                                                        COUNT(word) AS frequency 
                                                FROM text_handle.words_positions
                                                WHERE article_id = %s
                                                GROUP BY word""",
                                           (article_id,))
            self.db_handler.connection.commit()
            return self.db_handler.cursor.fetchall()

    def get_total_articles(self):
        """
        Get the total number of articles in the database.

        Returns:
            int: The total number of articles.
        """
        self.db_handler.cursor.execute("SELECT COUNT(*) FROM art_info.articles")
        return self.cursor.fetchone()[0]



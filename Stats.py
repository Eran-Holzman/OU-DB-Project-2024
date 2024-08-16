############################################################################################################
#              This module is responsible for calculating db statistics                                    #
#              The methods in this class implement the last requirements in the assignment                 #
############################################################################################################
from DB_handler import DB_handler


class Stats:
    def __init__(self):
        self.db_handler = DB_handler()

    # Returns a table with 2 columns, the word and the length of word.
    # This applies to all words in the database.
    def num_of_chars_per_word(self):
        self.db_handler.cursor.execute("""SELECT word, char_length(word) as word_length 
                                          FROM text_handle.words
                                          ORDER BY word_length""")
        self.db_handler.connection.commit()
        return self.db_handler.cursor.fetchall()

    # Returns the average number of characters per word in the database.
    def avg_num_of_chars_per_word(self):
        self.db_handler.cursor.execute("SELECT ROUND(AVG(char_length(word)),2) "
                                       "FROM text_handle.words")
        self.db_handler.connection.commit()
        return self.db_handler.cursor.fetchall()[0][0]

    # Returns a table with 2 columns, the word and the length of word.
    # This applies to all words in the article.
    def num_of_chars_per_word_in_article(self, article_title):
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

    # Returns the average number of characters per word in the article.
    def avg_num_of_chars_per_word_in_article(self, article_title):
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

    # Returns the total number of characters for EACH line in the article.
    # This INCLUDES spaces.
    def num_of_characters_in_line(self, article_title):
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

    # Returns the average number of characters for EACH line in the article.
    def avg_of_characters_in_line(self, article_title):
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

    # Returns the total number of characters in a paragraph
    def num_of_chars_in_paragraph(self, article_title):
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

    # Returns the average number of characters in a paragraph
    def avg_chars_in_paragraph(self, article_title):
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

    # Returns the total number of characters in the article
    def num_of_chars_in_article(self, article_title):
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

    # Returns the number of characters in the entire database(Of all the articles)
    def num_of_chars_in_db(self):
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

    # Returns the total number of words in the db)
    def num_of_words_in_db(self):
        self.db_handler.cursor.execute("""SELECT COUNT(word_id)
                                          FROM text_handle.words""")
        self.db_handler.connection.commit()
        return self.db_handler.cursor.fetchall()

    # Returns the total number of words in the article
    def num_of_words_in_article(self, article_title):
        article_id_full = self.db_handler.get_article_id_from_title(article_title)
        if article_id_full:
            article_id = article_id_full[0][0]
            self.db_handler.cursor.execute("""SELECT COUNT(word)
                                              FROM text_handle.words_positions
                                              WHERE article_id = %s""", (article_id,))
            self.db_handler.connection.commit()
            return self.db_handler.cursor.fetchall()

    # Returns the total number of words in the paragraph
    def num_of_words_in_paragraph(self, article_title):
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

    # Returns the average number of words in the paragraph
    def avg_words_in_paragraph(self, article_title):
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

    # Returns the total number of words in the line
    def num_of_words_in_line(self, article_title):
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

    # Returns a frequency list of the words in the entire database(Meaning all the articles)
    def frequency_list_db(self):
        self.db_handler.cursor.execute("""  SELECT ROW_NUMBER() OVER 
                                            (ORDER BY word) AS row_number, word, COUNT(word) AS frequency 
                                            FROM text_handle.words_positions
                                            GROUP BY word""")
        self.db_handler.connection.commit()
        return self.db_handler.cursor.fetchall()

    # Returns a frequency list of the words in the article
    def frequency_list_article(self, article_title):
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




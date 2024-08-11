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
        self.db_handler.cursor.execute("SELECT word, char_length(word) as word_length FROM text_handle.words")
        self.db_handler.connection.commit()
        res = self.db_handler.cursor.fetchall()

    # Returns the average number of characters per word in the database.
    def avg_num_of_chars_per_word(self):
        self.db_handler.cursor.execute("SELECT ROUND(AVG(char_length(word)),2) "
                                       "FROM text_handle.words")
        self.db_handler.connection.commit()
        return self.db_handler.cursor.fetchall()

    # Returns a table with 2 columns, the word and the length of word.
    # This applies to all words in the article.
    def num_of_chars_per_word_in_article(self, article_title):
        article_id = self.db_handler.get_article_id_from_title(article_title)
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
        article_id = self.db_handler.get_article_id_from_title(article_title)
        self.db_handler.cursor.execute("""
                                        SELECT 
                                            SELECT ROUND(AVG(char_length(w.word)),2)
                                        FROM 
                                            text_handle.words w,
                                            unnest(w.occurrences) as o(article_id, positions)
                                        WHERE 
                                            o.article_id = %s  
                                        """, (article_id,))
        self.db_handler.connection.commit()
        return self.db_handler.cursor.fetchall()


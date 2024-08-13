############################################################################################################
#              This module is responsible for building text from the database, including                   #
#                     building the entire text, building index list and context                            #
#              The methids in this class implement the 4th, 5th, 6th and 11th                              #
#                               requirements of the assignment                                             #
############################################################################################################
import streamlit as st
import pandas as pd
from DB_handler import DB_handler
from collections import defaultdict
import re
import ast

class TextBuilder:
    def __init__(self):
        self.db_handler = DB_handler()

    def build_entire_text(self, article_title):
        text_arr = []
        art_id_full = self.db_handler.get_article_id_from_title(article_title)
        if len(art_id_full) == 0:
            return None
        else:
            article_id = art_id_full[0][0]
        self.db_handler.cursor.execute("""SELECT a.date, r.first_name, r.last_name 
                                          FROM art_info.articles a JOIN art_info.reporters r 
                                          ON a.reporter_id = r.reporter_id 
                                          WHERE a.article_id = %s """,
                                         (article_id, ))
        self.db_handler.connection.commit()
        date_of_issue, rep_f_name, rep_last_name = self.db_handler.cursor.fetchall()[0]
        rep_full_name = rep_f_name + " " + rep_last_name
        self.db_handler.cursor.execute( """ SELECT 
                                                w.word,
                                                pos.paragraph_number,
                                                pos.line_number,
                                                pos.position_in_line,
                                                pos.starting_chars,
                                                pos.finishing_chars
                                            FROM 
                                                text_handle.words w,
                                                unnest(w.occurrences) as o(article_id, positions),
                                                unnest(o.positions) as pos(paragraph_number, line_number, 
                                                position_in_line, starting_chars, finishing_chars)
                                            WHERE 
                                                o.article_id = %s
                                                order by pos.paragraph_number, pos.line_number, pos.position_in_line; 
                                                """, (article_id, ))
        self.db_handler.connection.commit()
        for row in self.db_handler.cursor:
            text_arr.append((row[0], row[1], row[2], row[3], row[4], row[5]))
        final_text = ""
        for tup in text_arr:
            if tup[3] == 1:
                final_text += f"{tup[4]}" + f"{tup[0]}" + f"{tup[5]}"
            else:
                final_text += " " + f"{tup[4]}" + f"{tup[0]}" + f"{tup[5]}"
        return article_title, date_of_issue, rep_full_name, final_text

    def all_words(self):
        self.db_handler.cursor.execute(" SELECT word "
                                       " from text_handle.words"
                                       " order by word ")
        self.db_handler.connection.commit()
        return self.db_handler.cursor.fetchall()

    def all_words_in_article(self, article_title):
        article_id = self.db_handler.get_article_id_from_title(article_title)[0][0]
        self.db_handler.cursor.execute(" SELECT word "
                                       " from text_handle.words, unnest(occurrences) AS occ "
                                       " WHERE (occ).article_id = %s"
                                       " order by word ", (article_id,))
        self.db_handler.connection.commit()
        return self.db_handler.cursor.fetchall()

    def build_context(self, article_title, word):
        res =[]
        lines_arr = []
        article_id = self.db_handler.get_article_id_from_title(article_title)[0][0]
        word_id = self.db_handler.get_word_id_from_word(word)
        # self.db_handler.cursor.execute( """ SELECT
        #                                         pos.paragraph_number,
        #                                         pos.line_number
        #                                     FROM
        #                                         text_handle.words w,
        #                                         unnest(w.occurrences) as o(article_id, positions),
        #                                         unnest(o.positions) as pos(paragraph_number, line_number,
        #                                         position_in_line, starting_chars, finishing_chars)
        #                                     WHERE
        #                                         o.article_id = %s and word_id = %s """,
        #                                 (article_id, word_id))
        self.db_handler.cursor.execute( """ SELECT 
                                                paragraph_number,
                                                line_number
                                            FROM 
                                                text_handle.words_positions
                                            WHERE 
                                                article_id = %s and word_id = %s """,
                                        (article_id, word_id))
        self.db_handler.connection.commit()
        for row in self.db_handler.cursor:
            lines_arr.append((row[0], row[1]))
        for line in lines_arr:
            query = """
                    SELECT 
                        word,
                        paragraph_number,
                        line_number,
                        position_in_line,
                        starting_chars,
                        finishing_chars
                    FROM 
                        text_handle.words_positions
                    WHERE 
                        article_id = %s and paragraph_number = %s and line_number in (%s,%s,%s)
                        order by paragraph_number, line_number, position_in_line;
            """
            self.db_handler.cursor.execute(query, (article_id,line[0],line[1]-1,line[1],line[1]+1))
            self.db_handler.connection.commit()
            result = self.db_handler.cursor.fetchall()
            text_arr = []
            for row in result:
                text_arr.append((row[0], row[1], row[2], row[3], row[4], row[5]))
            final_context = ""
            for tup in text_arr:
                if tup[3] == 1:
                    final_context += f"{tup[4]}" + f"{tup[0]}" + f"{tup[5]}"
                else:
                    final_context += " " + f"{tup[4]}" + f"{tup[0]}" + f"{tup[5]}"
            res.append(final_context)
        return res

    # An index is defined as the position of the word in the article.
    # The position consists of the paragraph number, the line number and the position in the line.
    def build_words_index(self, article_title):
        art_id_full = self.db_handler.get_article_id_from_title(article_title)
        if len(art_id_full) == 0:
            return None
        else:
            article_id = art_id_full[0][0]
        self.db_handler.cursor.execute( """ SELECT 
                                                word,
                                                paragraph_number,
                                                line_number,
                                                position_in_line
                                            FROM 
                                                text_handle.words_positions
                                            WHERE 
                                                article_id = %s
                                                order by word, paragraph_number, 
                                                line_number, position_in_line; """,
                                        (article_id, ))
        self.db_handler.connection.commit()
        words_index = self.db_handler.cursor.fetchall()

        occurrences_dict = defaultdict(list)
        for row in words_index:
            word, paragraph_number, line_number, position_in_line = row
            occurrence = (paragraph_number, line_number, position_in_line)
            occurrences_dict[word].append(occurrence)
        index_arr = []
        for word, occurrences in occurrences_dict.items():
            index_arr.append((word, occurrences))

        return index_arr

    def handle_indexes(self, flag):
        article_title = st.selectbox("Please select an article ",
                                     self.create_article_titles_array())
        if st.button("View") and article_title:
            words_index = self.build_words_index(article_title)
            if flag == 'article':
                if len(article_title) != 0 and words_index is None:
                    st.write("Invalid article title")
                elif words_index:
                    df = pd.DataFrame(words_index, columns=["Word", "Index"])
                    st.subheader(f"The words index in the article '{article_title}': ")
                    st.write("* Please note that the index is a paragraph number, row number and position in the row")
                    st.dataframe(df, hide_index=True, width=1000)
                elif article_title and words_index is None:
                    st.write("The article is empty")
                else:
                    st.write("Article not found.")
                if st.button("Start indexes view from the beginning"):
                    self.handle_indexes()
            elif flag == 'group':
                group_words_index = self.build_group_words_index(article_title)
                if len(article_title) != 0 and words_index is None:
                    st.write("Invalid article title")
                elif words_index:
                    df = pd.DataFrame(group_words_index, columns=["Word", "Index"])
                    st.subheader(f"The words index in the article '{article_title}': ")
                    st.write("* Please note that the index is a paragraph number, row number and position in the row")
                    st.dataframe(df, hide_index=True, width=1000)
                elif article_title and words_index is None:
                    st.write("The article is empty")
                else:
                    st.write("Article not found.")
                if st.button("Start indexes view from the beginning"):
                    self.handle_indexes()

    def build_group_words_index(self, article_title, words):
        article_id = self.db_handler.get_article_id_from_title(article_title)[0][0]
        query = """
            SELECT 
                word,
                paragraph_number,
                line_number,
                position_in_line
            FROM 
                text_handle.words_positions
            WHERE 
                article_id = %s
                AND word = ANY(%s)
                order by paragraph_number, line_number, position_in_line;
        """
        self.db_handler.cursor.execute(query, (article_id, words))
        self.db_handler.connection.commit()
        group_words_index = self.db_handler.cursor.fetchall()
        st.subheader(f"The words index for this group in the article '{article_title}': ")
        st.write("* Please note that the index is a paragraph number, row number and position in the row")
        for index in group_words_index:
            col1, col2, col3 = st.columns(3, vertical_alignment="center")
            with col1:
                st.write(' ')
            with col2:
                st.write((index[1]), (index[2]), (index[3]))
            with col3:
                st.write(' ')
        if st.button("View index per word"):
            occurrences_dict = defaultdict(list)
            for row in group_words_index:
                word, paragraph_number, line_number, position_in_line = row
                occurrence = (paragraph_number, line_number, position_in_line)
                occurrences_dict[word].append(occurrence)
            index_arr = []
            for word, occurrences in occurrences_dict.items():
                index_arr.append((word, occurrences))
            df = pd.DataFrame(index_arr, columns=["Word", "Index"])
            st.subheader(f"The words index for this group in the article '{article_title}': ")
            st.write("* Please note that the index is a paragraph number, row number and position in the row")
            st.dataframe(df, hide_index=True, width=1000)

    def create_article_titles_array(self):
        articles_tup_arr = self.db_handler.get_all_article_titles()
        ret = ["Please select"]
        for article_tup in articles_tup_arr:
            ret.append(article_tup[0])
        return ret

    def handle_all_words_in_article(self):
        article_title = st.selectbox("Please select an article ",
                                     self.create_article_titles_array())
        if st.button("View") and article_title:
            words = self.all_words_in_article(article_title)
            if words:
                st.subheader(f"All the words in the article '{article_title}' are: ")
                for word in words:
                    col1, col2, col3 = st.columns(3, vertical_alignment="center")
                    with col1:
                        st.write(word[0])
                    with col2:
                        with st.popover("Show Context", help=f"Click for '{word[0]}' context in the article"):
                            st.markdown(f"context/s for {word[0]}:")
                            context_list = self.build_context(article_title, word[0])
                            i = 0
                            for context in context_list:
                                i+=1
                                st.markdown(f"context {i}:")
                                st.markdown(f"{context.replace('\n', '  \n')}")
                            st.markdown(f"the word is '{word[0]}' and article name is '{article_title}'")

            elif article_title and words is None:
                st.error("The article is empty")
            else:
                st.error("Article not found.")

    def handle_all_words(self):
        words = self.all_words()
        if words:
            st.subheader("All the words in the database are: ")
            for word_tup in words:
                st.write(word_tup[0])
            st.write(words)
        else:
            st.error("The database has no words yet.")

    def handle_article_view(self):
        article_title = st.selectbox("Please select an article ",
                                     self.create_article_titles_array())
        if st.button("View") and article_title:
            article = self.build_entire_text(article_title)
            if article:
                st.write(f"Title: {article[0]}")
                st.write(f"Date: {article[1]}")
                st.write(f"Reporter: {article[2]}")
                st.write("Content:")
                final_text = article[3].replace('\n', '  \n')
                st.write(final_text)
            else:
                st.error("Article not found.")


















"""
This module handles word group operations for the article processing system.
It provides functionality for creating, managing, and viewing word groups,
as well as adding words to these groups.

The WordGroup class interacts with the database to perform these operations
and provides methods for handling the Streamlit UI for word group functionalities.
"""

import streamlit as st
from db_handler import *
from text_builder import TextBuilder


def make_arr_from_tuparr(tup_arr):
    """
    Convert a list of tuples to a list of strings.

    Args:
        tup_arr (List[tuple]): A list of tuples, where each tuple contains a single string.

    Returns:
         List[str]: A list of strings extracted from the tuples.
    """
    ret = []
    for tup in tup_arr:
        ret.append(tup[0])
    return ret


class WordGroup:
    """
    A class for managing word groups in the article processing system.

    This class provides methods for creating word groups, adding words to groups,
    retrieving group information, and handling the Streamlit UI for group-related operations.
   """

    def __init__(self):
        """Initialize the WordGroup with database handler and text builder."""
        self.db_handler = DBHandler()
        self.tb = TextBuilder()

    def get_group_id(self, group_description):
        """
        Get the ID of a group based on its description.

        Args:
            group_description (str): The description of the group.

        Returns:
            Optional[int]: The group ID if found, None otherwise.
        """
        self.db_handler.cursor.execute("SELECT group_id FROM text_handle.word_groups WHERE group_description = %s",
                                       (group_description,))
        self.db_handler.connection.commit()
        group_id = self.db_handler.cursor.fetchall()
        if len(group_id) == 0:
            return None
        else:
            return group_id[0][0]

    def create_group(self, group_description):
        """
        Create a new word group in the database.

        Args:
            group_description (str): The description of the new group.
        """
        self.db_handler.cursor.execute(" INSERT INTO text_handle.word_groups (group_description) "
                                       " VALUES (%s) ", (group_description,))
        self.db_handler.connection.commit()

    def add_word_to_group(self, group_id, word_id):
        """
        Add a word to a specific group in the database.

        Args:
            group_id (int): The ID of the group.
            word_id (int): The ID of the word to add.
        """
        self.db_handler.cursor.execute("UPDATE text_handle.word_groups SET word_ids = array_append(word_ids, %s) "
                                       " WHERE group_id = %s", (word_id, group_id))
        self.db_handler.connection.commit()

    def get_group(self, group_description):
        """
        Get all words in a specific group.

         Args:
              group_description (str): The description of the group.

         Returns:
              List[str]: A list of words in the group.
        """
        self.db_handler.cursor.execute("SELECT word_ids FROM text_handle.word_groups WHERE group_description = %s",
                                       (group_description,))
        self.db_handler.connection.commit()
        word_ids = self.db_handler.cursor.fetchall()
        words = []
        for word_id in word_ids[0][0]:
            self.db_handler.cursor.execute("SELECT word FROM text_handle.words WHERE word_id = %s", (word_id,))
            self.db_handler.connection.commit()
            word = self.db_handler.cursor.fetchall()
            words.append(word[0][0])
        return words

    def get_all_groups(self):
        """
        Get all group descriptions from the database.

        Returns:
            List[str]: A list of all group descriptions, with "Please select" as the first option.
        """
        self.db_handler.cursor.execute("SELECT group_description FROM text_handle.word_groups")
        self.db_handler.connection.commit()
        groups = self.db_handler.cursor.fetchall()
        ret = ["Please select"]
        ret.extend(make_arr_from_tuparr(groups))
        return ret

    def is_word_in_group(self, group_id, word_id):
        """
        Check if a word is already in a specific group.

        Args:
          group_id (int): The ID of the group.
          word_id (int): The ID of the word.

        Returns:
          bool: True if the word is in the group, False otherwise.
        """
        query = """
        SELECT *
        FROM text_handle.word_groups
        WHERE group_id = %s AND %s = ANY(word_ids);
        """
        self.db_handler.cursor.execute(query, (group_id, word_id))
        self.db_handler.connection.commit()
        if self.db_handler.cursor.fetchall():
            return True
        else:
            return False

    def handle_group_creation(self):
        """Handle the Streamlit UI for creating a new word group."""
        group_description = st.text_input("Enter group description")
        group_id = self.get_group_id(group_description)
        if group_id and st.button("Create group") and len(group_description) != 0:
            st.error("Group already exists.")
        elif group_id is None and st.button("Create group") and len(group_description) != 0:
            try:
                self.create_group(group_description)
                st.success(f"Group {group_description} created successfully.")
            except Exception as e:
                st.error("Error while creating the group.")

    def handle_group_addition(self):
        """Handle the Streamlit UI for adding words to a group."""
        group_description = st.selectbox("Please select a group ",
                                         self.get_all_groups())
        if group_description != "Please select":
            group_id = self.get_group_id(group_description)
            if group_id:
                add_type = st.selectbox("How would you like to add the word to the group?",
                                        ["Please select", "Type word", "Select from a list of words"])
                if add_type == "Type word":
                    word = st.text_input("Please enter the word you would like to add to the group.")
                    word_id = self.db_handler.get_word_id_from_word(word)
                    is_in_group = self.is_word_in_group(group_id, word_id)
                    if is_in_group:
                        st.error(f"The word {word} is already in the group.")
                    else:
                        if st.button("Add word to group"):
                            if word_id == -1:
                                st.error("The word you're trying to enter is not any of the articles.")
                            else:
                                try:
                                    self.add_word_to_group(group_id, word_id)
                                    st.success(f"The word {word} has been added to the group.")
                                except Exception as e:
                                    st.error("Error while adding the word to the group.")
                elif add_type == "Select from a list of words":
                    word_options = ["Please select"]
                    word_options.extend(make_arr_from_tuparr(self.tb.all_words()))
                    word = st.selectbox(f"Which word would you like to add to the group {group_description}?",
                                        word_options)
                    if word != "Please select":
                        word_id = self.db_handler.get_word_id_from_word(word)
                        is_in_group = self.is_word_in_group(group_id, word_id)
                        if is_in_group:
                            st.error(f"The word {word} is already in the group.")
                        else:
                            if word_id == -1:
                                st.error("The word you're trying to enter is not any of the articles.")
                            else:
                                try:
                                    self.add_word_to_group(group_id, word_id)
                                    st.success(f"The word {word} has been added to the list.")
                                except Exception as e:
                                    st.error("Error while adding the word to the group.")
            elif not group_id and group_description:
                st.error("Group not found.")

    def handle_my_groups(self):
        """Handle the Streamlit UI for viewing words in a group."""

        groups = self.get_all_groups()
        group = st.selectbox("My groups:", groups)
        if group != "Please select":
            words = self.get_group(group)
            if words:
                st.subheader(f"Words in group {group}:")
                for word in words:
                    st.write(word)
            else:
                st.write("Group is empty.")

    def group_index(self):
        """Handle the Streamlit UI for viewing group indexes in articles."""
        st.subheader("Group indexes:")
        group_description = st.selectbox("Please select a group ",
                                         self.get_all_groups())
        if group_description != "Please select":
            group_id = self.get_group_id(group_description)
            if group_id:
                words = self.get_group(group_description)
                if words:
                    article_title = st.selectbox("Please select an article", self.tb.create_article_titles_array())
                    if article_title and article_title != "Please select":
                        self.tb.build_group_words_index(article_title, words)
                else:
                    st.write("Group is empty.")
            else:
                st.error("Group not found.")

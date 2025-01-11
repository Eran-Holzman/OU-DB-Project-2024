"""
This module implements the Streamlit-based user interface for the News Article Database application.
It provides a graphical interface for various functionalities including article management,
searching, viewing, word group operations, phrase handling, and statistical analysis.
"""

import streamlit as st
from db_handler import *
from article import *
from search_wizard import *
from word_group import *
from phrases import *
from collections import Counter
import plotly.express as px
from stats import Stats
from pandas import *


def count_sentences(text):
    """
    Count the number of sentences in a given text.

    Args:
        text (str): The input text.

    Returns:
        int: The number of sentences in the text.
    """
    pattern = r'[.]'
    sentences = re.split(pattern, text)
    sentences = [s.strip() for s in sentences if s.strip()]
    return len(sentences)


class StreamlitUI:
    """
    Implements the Streamlit-based user interface for the News Article Database application.

    This class provides methods for different functionalities of the application,
    including adding articles, searching, viewing, managing word groups, and analyzing statistics.
    """

    def __init__(self):
        """
        Initialize the StreamlitUI with necessary components.
        """
        self.database = DBHandler()
        self.sw = SearchWizard()
        self.tb = TextBuilder()
        self.wg = WordGroup()
        self.ph = Phrases()

    def run(self):
        """
        Run the main Streamlit application.

        This method sets up the sidebar menu and handles navigation between different functionalities.
        """
        st.title("News Article Database")

        menu = ["Home", "Add Article", "Search", "View", "Word groups",
                "Phrases", "Word Statistics"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Home":
            self.show_home()
        elif choice == "Add Article":
            self.add_article()
        elif choice == "Search":
            self.search()
        elif choice == "View":
            self.view()
        elif choice == "Word groups":
            self.word_groups()
        elif choice == "Phrases":
            self.phrases()
        elif choice == "Word Statistics":
            self.word_statistics()

    def show_home(self):
        """Display the home page of the application."""
        st.write("Welcome to the News Article Database!")
        st.write("Use the sidebar to navigate through different functions.")
        st.subheader("My articles")
        all_articles = self.database.get_all_articles()
        df = pd.DataFrame(all_articles, columns=["", "Newspaper", "Article", "Date"])
        st.dataframe(df, hide_index=True, width=1000)

    def add_article(self):
        """Handle the functionality for adding a new article to the database."""
        st.subheader("Add a New Article")

        uploaded_file = st.file_uploader("Choose a .txt file", type="txt")

        if uploaded_file is not None:
            try:
                full_text_file = uploaded_file.read().decode('utf-8')
                article = Article(full_text_file)
                st.write(f"Title: {article.get_title()}")
                st.write(f"Authors: {article.get_authors()}")
                st.write(f"Newspaper name: {article.get_newspaper()}")
                st.write(f"Date: {article.get_date()}")
                st.write("--------------------")
                st.write("Content Preview:")
                st.write(article.get_content())
                if st.button("Add Article"):
                    article.process_content()
                    st.success("Article added successfully!")
            except Exception as e:
                st.error("""Error processing file. One of the following could be the reason:  \n
1. It is possible that the article is already in the system.  \n
2. There file is not in the correct format.  \n
3. The file's structure is incorrect(For example, the date is not in the format YYYY-MM-DD).""")
        else:
            st.write("Please upload a .txt file to add an article.")

    def search(self):
        """Handle the search functionality, allowing users to search for articles or words."""
        st.subheader("Search")
        search_type = st.selectbox("What would you like to search for?", ["Please select", "Articles", "Word", ])
        if search_type == "Articles":
            self.search_articles()
        elif search_type == "Word":
            self.search_word()

    def search_articles(self):
        """Handle the functionality for searching articles by different criteria."""
        st.subheader("Search Articles")
        search_type = st.selectbox("Search articles by", ["Please select", "reporter", "newspaper", "date", "word"])
        if search_type == "reporter":
            self.sw.handle_search_reporter_articles()
        elif search_type == "newspaper":
            self.sw.handle_search_newspaper_articles()
        elif search_type == "date":
            self.sw.handle_search_date_articles()
        elif search_type == "word":
            self.sw.handle_search_word_articles()

    def search_word(self):
        """Handle the functionality for searching a specific word in an article."""
        st.subheader("Search Word")
        article_title = st.text_input("Enter article title")
        paragraph_number = st.text_input("Enter paragraph number")
        line_number = st.text_input("Enter line number")
        position_in_line = st.text_input("Enter position in line")
        if st.button("Search"):
            if len(article_title) != 0 and len(paragraph_number) != 0 and len(line_number) != 0 and len(
                    position_in_line) != 0:
                word = self.sw.search_word_at_position(article_title, paragraph_number, line_number, position_in_line)
                if word:
                    st.write(
                        f"The word at position ({paragraph_number}, {line_number}, {position_in_line}) in the "
                        f"article '{article_title}' is: {word}")
                else:
                    st.write("Word not found.")
            else:
                st.write("Please fill all fields.")

    def view(self):
        """Handle the view functionality, allowing users to view different aspects of the database."""
        st.subheader("View")
        view_type = st.selectbox("What do you want to view?",
                                 ["Please select", "Article", "All words in db", "All words in article",
                                  "Index of all words in article"])
        if view_type == "Article":
            self.tb.handle_article_view()
        elif view_type == "All words in db":
            self.tb.handle_all_words()
        elif view_type == "All words in article":
            self.tb.handle_all_words_in_article()
        elif view_type == "Index of all words in article":
            self.tb.handle_indexes('article')

    def word_groups(self):
        """Handle the word group functionality, allowing users to manage word groups."""
        st.subheader("Word Groups")
        wg_type = st.selectbox("What would you like to do?",
                               ["Please select", "Create group", "Add word to existing group", "My groups",
                                "Group index"])
        if wg_type == "Create group":
            self.wg.handle_group_creation()
        elif wg_type == "Add word to existing group":
            self.wg.handle_group_addition()
        elif wg_type == "My groups":
            self.wg.handle_my_groups()
        elif wg_type == "Group index":
            self.wg.group_index()

    def phrases(self):
        """Handle the phrases functionality, allowing users to define and search for phrases."""
        st.subheader("Phrases")
        choice = st.selectbox("What would you like to do?", ["Please select", "Define phrase manually",
                                                             "manual phrase search", "phrases in text"])
        if choice == "Define phrase manually":
            self.ph.manual_phrase_definition()
        elif choice == "phrases in text":
            self.ph.phrases_in_text()
        elif choice == "manual phrase search":
            self.ph.manual_phrase_search()

    def word_statistics(self):
        """Handle the word statistics functionality, providing various statistics about words in articles."""
        st.subheader("Word Statistics")

        article_titles = self.tb.create_article_titles_array()
        selected_title = st.selectbox("Select an article or leave blank for all articles", article_titles)

        if st.button("Get Statistics"):
            stats = Stats()  # Create an instance of the Stats class

            if selected_title != "Please select":
                # Statistics for a specific article
                words = stats.num_of_chars_per_word_in_article(selected_title)
                if not words:
                    st.error(f"No words found for article '{selected_title}'. The article might not exist or be empty.")
                    return
                st.write(f"Statistics for article '{selected_title}':")
                page_count = 1  # A Single article is always one page

                # Article-specific statistics
                char_count = stats.num_of_chars_in_article(selected_title)
                word_count = stats.num_of_words_in_article(selected_title)[0][0]
                avg_chars_per_word = stats.avg_num_of_chars_per_word_in_article(selected_title)
                avg_words_per_line = stats.avg_words_in_line(selected_title)[0][0]
                avg_chars_per_line = stats.avg_of_characters_in_line(selected_title)
                avg_words_per_paragraph = stats.avg_words_in_paragraph(selected_title)[0][0]
                avg_chars_per_paragraph = stats.avg_chars_in_paragraph(selected_title)

                # Get full article text for sentence counting
                article = self.tb.build_entire_text(selected_title)
                content = article[3]
                sentence_count = count_sentences(content)
            else:
                # Statistics for all articles
                words = stats.num_of_chars_per_word()
                if not words:
                    st.error("No words found in the database. The database might be empty.")
                    return
                st.write("Statistics for all articles:")

                db_handler = DBHandler()

                # Database-wide statistics
                char_count = stats.num_of_chars_in_db()[0][0]
                word_count = stats.num_of_words_in_db()[0][0]
                avg_chars_per_word = stats.avg_num_of_chars_per_word()
                page_count = db_handler.get_total_articles()  # Total number of articles (each article is one page)

                # These are not available for all articles combined, so we'll skip them
                avg_words_per_line = None
                avg_chars_per_line = None
                avg_words_per_paragraph = None
                avg_chars_per_paragraph = None
                sentence_count = None

            # Character statistics
            st.subheader("Character Statistics")
            st.write(f"Total characters: {char_count}")
            st.write(f"Average characters per word: {avg_chars_per_word:.2f}")
            if avg_chars_per_line:
                st.write(f"Average characters per line: {avg_chars_per_line:.2f}")
            if avg_chars_per_paragraph:
                st.write(f"Average characters per paragraph: {avg_chars_per_paragraph:.2f}")
            st.write("----------------------")

            # Word statistics
            st.subheader("Word Statistics")
            st.write(f"Total words: {word_count}")
            if avg_words_per_line:
                st.write(f"Average words per line: {avg_words_per_line:.2f}")
            if avg_words_per_paragraph:
                st.write(f"Average words per paragraph: {avg_words_per_paragraph:.2f}")
            st.write(f"Average words per page: {word_count / page_count:.2f}")
            st.write("----------------------")

            # Sentence statistics (only for single article)
            if sentence_count:
                st.subheader("Sentence Statistics")
                st.write(f"Total sentences: {sentence_count}")
                st.write(f"Average sentences per page: {sentence_count / page_count:.2f}")
                st.write("----------------------")

            # Page statistics (only for all articles)
            if selected_title == "Please select":
                st.subheader("Page Statistics")
                st.write(f"Total pages: {page_count}")
                st.write("----------------------")

            st.subheader("Word Frequency")
            if selected_title != "Please select":
                word_freq = stats.frequency_list_article(selected_title)
                word_freq.sort(key=lambda x: x[2], reverse=True)  # Sort by frequency (descending)
                freq_df = pd.DataFrame([(word, freq) for _, word, freq in word_freq], columns=['Word', 'Frequency'])
                st.write(f"All words in article '{selected_title}' (sorted by frequency):")
            else:
                word_freq = stats.frequency_list_db()
                word_freq.sort(key=lambda x: x[2], reverse=True)  # Sort by frequency (descending)
                freq_df = pd.DataFrame([(word, freq) for _, word, freq in word_freq], columns=['Word', 'Frequency'])
                st.write("All words across all articles (sorted by frequency):")
            st.dataframe(freq_df, hide_index=True)
            st.write("----------------------")
            # Word length distribution
            st.subheader("Word Length Distribution")
            word_lengths = [len(word) for _, word, _ in word_freq]
            word_examples = {len(word): word for _, word, _ in word_freq}

            length_freq = Counter(word_lengths)
            length_df = pd.DataFrame(sorted(length_freq.items()), columns=['Word Length', 'Frequency'])

            # Filter out lengths with zero frequencies
            length_df = length_df[length_df['Frequency'] > 0]

            # Add example words to the dataframe
            length_df['Example'] = length_df['Word Length'].map(word_examples)

            fig = px.bar(length_df, x='Word Length', y='Frequency',
                         title='Distribution of Word Lengths',
                         labels={'Word Length': 'Number of Characters', 'Frequency': 'Number of Words'},
                         hover_data=['Example'])

            fig.update_layout(
                xaxis_title="Number of Characters in Word",
                yaxis_title="Number of Words",
                xaxis=dict(tickmode='linear', dtick=1)
            )

            # Display the plot
            st.plotly_chart(fig, use_container_width=True)

import streamlit as st
from Article import Article
from SearchWizard import *
from WordGroup import *
from Phrases import *

def count_sentences(text):
    # pattern = r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])\s*$'
    pattern = r'[.]' # Split by period
    sentences = re.split(pattern, text)
    print("+++++++++++++++++++++++++++++++")
    print(text)
    print("------------------------")
    print(sentences)
    print("+++++++++++++++++++++++++++++++")

    # Filter out empty strings
    sentences = [s.strip() for s in sentences if s.strip()]
    return len(sentences)

class StreamlitUI:
    def __init__(self, database: DB_handler):
        self.database = DB_handler()
        self.sw = SearchWizard()
        self.tb = TextBuilder()
        self.wg = WordGroup()
        self.ph = Phrases()

    def run(self):
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
        st.write("Welcome to the News Article Database!")
        st.write("Use the sidebar to navigate through different functions.")

    def add_article(self):
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
                st.error('Error processing file. It is possible that the article is already in the system.')
        else:
            st.write("Please upload a .txt file to add an article.")

    def search(self):
        st.subheader("Search")
        search_type = st.selectbox("What would you like to search for?", ["Please select", "Articles", "Word", ])
        if search_type == "Articles":
            self.search_articles()
        elif search_type == "Word":
            self.search_word()

    def search_articles(self):
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
        st.subheader("Phrases")
        choice = st.selectbox("What would you like to do?", ["Please select", "Define phrase manually",
                                                             "manual phrase search", "phrases in text"])
        if choice == "Define phrase manually":
            self.ph.manual_phrase_definition()
        elif choice == "phrases in text":
            self.ph.phrases_in_text()
        elif choice == "manual phrase search":
            self.ph.manual_phrase_search()

    # def word_statistics(self):
    #     st.subheader("Word Statistics")
    #     title = st.text_input("Enter article title (leave blank for all articles)")
    #
    #     if st.button("Get Statistics"):
    #         if title:
    #             words = self.tb.all_words_in_article(title)  # Need to be changed!~!!!!
    #             print("WORDS::", words)
    #             # add the word cloud::::(and remove the 'stop' words)
    #             if not words:
    #                 st.error(f"No words found for article '{title}'. The article might not exist or be empty.")
    #                 return
    #             st.write(f"Statistics for article \n \n '{title}':")
    #             page_count = 1  # Single article is always one page
    #         else:
    #             words = self.tb.all_words()  # Need to be changed!~!!!!
    #             if not words:
    #                 st.error("No words found in the database. The database might be empty.")
    #                 return
    #             st.write("Statistics for all articles:")
    #             page_count = len(set([word[1] for word in words]))  # Count unique articles
    #
    #         # Convert words to a list of strings
    #         word_list = [word[0] for word in words]
    #         # text = " ".join(word_list)
    #         article = self.tb.build_entire_text(title)
    #         content = article[3]
    #
    #         # Calculate statistics
    #         char_count = sum(len(word) for word in word_list)
    #         word_count = len(word_list)
    #         sentence_count = count_sentences(content)
    #
    #         # Character statistics
    #         st.subheader("Character Statistics")
    #         st.write(f"Total characters: {char_count}")
    #         st.write(f"Average characters per word: {char_count / word_count:.2f}")
    #         if sentence_count > 0:
    #             st.write(f"Average characters per sentence: {char_count / sentence_count:.2f}")
    #         st.write(f"Average characters per page: {char_count / page_count:.2f}")
    #         st.write("----------------------")
    #
    #         # Word statistics
    #         st.subheader("Word Statistics")
    #         st.write(f"Total words: {word_count}")
    #         if sentence_count > 0:
    #             st.write(f"Average words per sentence: {word_count / sentence_count:.2f}")
    #         st.write(f"Average words per page: {word_count / page_count:.2f}")
    #         st.write("----------------------")
    #
    #         # Sentence statistics
    #         st.subheader("Sentence Statistics")
    #         st.write(f"Estimated total sentences: {sentence_count}")
    #         st.write(f"Average sentences per page: {sentence_count / page_count:.2f}")
    #         st.write("----------------------")
    #
    #         # Page statistics
    #         st.subheader("Page Statistics")
    #         st.write(f"Total pages: {page_count}")
    #         st.write("----------------------")
    #
    #         # Word frequency
    #         st.subheader("Word Frequency")
    #         word_freq = Counter(word_list)
    #         top_words = word_freq.most_common(20)
    #
    #         freq_df = pd.DataFrame(top_words, columns=['Word', 'Frequency'])
    #         st.write("Top 20 most frequent words:")
    #         st.dataframe(freq_df, hide_index=True)
    #         st.write("----------------------")
    #
    #         # Word length distribution
    #         st.subheader("Word Length Distribution")
    #         word_lengths = [len(word) for word in word_list]
    #         length_freq = Counter(word_lengths)
    #         length_df = pd.DataFrame(sorted(length_freq.items()), columns=['Word Length', 'Frequency'])
    #
    #         # Filter out lengths with zero frequencies
    #         length_df = length_df[length_df['Frequency'] > 0]
    #         # Create a dictionary mapping word lengths to example words
    #         word_examples = {len(word): word for word in word_list}
    #         # Add example words to the dataframe
    #         length_df['Example'] = length_df['Word Length'].map(word_examples)
    #
    #         fig = px.bar(length_df, x='Word Length', y='Frequency',
    #                      title='Distribution of Word Lengths',
    #                      labels={'Word Length': 'Number of Characters', 'Frequency': 'Number of Words'},
    #                      hover_data=['Example'])
    #
    #         fig.update_layout(
    #             xaxis_title="Number of Characters in Word",
    #             yaxis_title="Number of Words",
    #             xaxis=dict(tickangle=0)
    #         )
    #
    #         # Display the plot
    #         st.plotly_chart(fig, use_container_width=True)
    #
    #
    #             st.write(f"{word}: {count}")

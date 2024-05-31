# import streamlit as st
# import newspaper
#
# import os
#
# st.title('News Article Summarizer')
# url = st.text_input('', placeholder='Enter the path of the news article file')
#
# # if file_path and os.path.isfile(file_path):
# #     with open(file_path, 'r', encoding='utf-8') as file:
# #         article_text = file.read()
# #     st.write(article_text)
#
#
# if url:
#     article = newspaper.Article(url)
#     article.download()
#
#     article.parse()
#     # article.nlp()
#     authors = article.authors
#     keywords = article.keywords
#     st.text(','.join(authors))
#     st.text(','.join(keywords))
#     # publish_date = article.publish_date
#     # word_count = article.text.split()
#     # st.write(article.summary)
#
#
# def parse_text(texti):
#     paragraphs = texti.split('\n\n')  # Split text into paragraphs
#
#     for p_index, paragraph in enumerate(paragraphs, start=1):
#         lines = paragraph.split('\n')  # Split paragraph into lines
#
#         for l_index, line in enumerate(lines, start=1):
#             words = line.split()  # Split line into words
#
#             for w_index, word in enumerate(words, start=1):
#                 print(f'Word: "{word}", Position: (Paragraph: {p_index}, Line: {l_index}, Word: {w_index})')
#
#
# # Test the function with your text
# text = """This is the first line of the first paragraph.
# This is the second line of the first paragraph.
#
# This is the first line of the second paragraph.
# This is the second line of the second paragraph."""
#
# parse_text(text)
import streamlit as st
import newspaper
import os
from collections import defaultdict

st.title('Eran & Omri News Article Summarizer')
url = st.text_input('', placeholder='Enter the path of the news article file')


def parse_text(texti):
    word_positions = defaultdict(list)
    paragraphs = texti.split('\n\n')  # Split text into paragraphs

    for p_index, paragraph in enumerate(paragraphs, start=1):
        lines = paragraph.split('\n')  # Split paragraph into lines

        for l_index, line in enumerate(lines, start=1):
            words = line.split()  # Split line into words

            for w_index, word in enumerate(words, start=1):
                word_positions[word].append((p_index, l_index, w_index))

    return word_positions


if url:
    try:
        article = newspaper.Article(url)
        article.download()
        article.parse()

        authors = article.authors
        publish_date = article.publish_date
        headline = article.title
        st.text('Authors: ' + ', '.join(authors))
        st.text('Publish Date: ' + str(publish_date))
        st.text('Headline: ' + headline)

        word_positions = parse_text(article.text)
        for word, positions in word_positions.items():
            st.text(f'Word: "{word}", Positions: {positions}')
            # print()
    except:
        st.error('Sorry, something went wrong')

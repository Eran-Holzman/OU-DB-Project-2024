# Handles text manipulation, file uploading, breaking down words, etc.
import re
from TextLoader import *
from typing import Dict, List, Tuple


def split_word(word):
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


def check_str_for_quotes(input_string):
    ret = (input_string.replace("'", "hhhaaa")
           .replace("’", "hhhbbb")
           .replace(r'-', 'hhhccc')
           .replace("/", "hhhddd")
           .replace("\\", "hhheee"))

    return ret


def is_only_none_alnum(word):
    for char in word:
        if char.isalnum():
            return False
    return True


class Article:
    def __init__(self, txt_file):
        lines = txt_file.split('\n')
        self.title = lines[0].strip()
        self.authors = lines[1].strip()
        self.newspaper = lines[2].strip()
        self.date = lines[3].strip()
        self.content = '\n'.join(lines[4:]).strip()
        self.words: Dict[str, List[Tuple[int, int, int, str, str]]] = {}
        self.tl = TextLoader()

    def process_content(self):
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
                        tup = (p_index, l_index, word_position, word_tuple[2] + '\n\n', word_tuple[0])
                    elif is_last_word_in_line:
                        tup = (p_index, l_index, word_position, word_tuple[2] + '\n', word_tuple[0])
                    else:
                        tup = (p_index, l_index, word_position, word_tuple[2], word_tuple[0])
                    if word_tuple[1] not in self.words:
                        self.words[word_tuple[1]] = []
                    self.words[word_tuple[1]].append(tup)
        reporter_id = self.tl.load_reporter(self.authors)
        np_id = self.tl.load_newspaper(self.newspaper)
        article_id = self.tl.load_article(np_id, self.title, self.date, reporter_id)
        self.tl.load_text(article_id, self.words)

    def print_words(self):
        print(f"Words Dictionary for article: {self.title}")
        for word, positions in self.words.items():
            print(f"Word: {word}")
            for pos in positions:
                print(f"  Position: (Paragraph: {pos[0]}, Line: {pos[1]}, Word: {pos[2]}), "
                      f"Previous punctuation: '{pos[3]}', Next punctuation: '{pos[4]}'")
            print()  # Empty line for readability

    def get_words_dictionary(self):
        return self.words

    def get_title(self):
        return self.title

    def get_authors(self):
        return self.authors

    def get_newspaper(self):
        return self.newspaper

    def get_date(self):
        return self.date

    def get_content(self):
        return self.content

    def get_words(self):
        return self.words

    def rebuild_content(self) -> str:
        sorted_words = sorted(
            [(word, pos) for word, positions in self.words.items() for pos in positions],
            key=lambda x: (x[1][0], x[1][1], x[1][2])
        )
        rebuilt_content = ""
        current_para = 0
        for word, (para_num, line_num, _, prev_punct, next_punct) in sorted_words:
            if para_num > current_para:
                rebuilt_content += "\n\n" if current_para > 0 else ""
                current_para = para_num
            rebuilt_content += f"{prev_punct}{word}{next_punct}"
        return rebuilt_content.strip()

        # Database interaction comment:
        """
        To rebuild the content from the database:
        Use TextBuilder.build_entire_text(self.title) to get the article content
        """

    def get_statistics(self):
        total_words = sum(len(positions) for positions in self.words.values())
        unique_words = len(self.words)
        most_common = sorted(self.words.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        avg_para_length = sum(len(p.split()) for p in self.content.split('\n\n')) / len(self.content.split('\n\n'))
        return {
            "total_words": total_words,
            "unique_words": unique_words,
            "most_common": most_common,
            "avg_para_length": avg_para_length
        }

        # Database interaction comment:
        """
        To get word statistics from the database:
        1. Use TextBuilder.all_words() to get all words in the database
        2. Use TextBuilder.all_words_in_article(article_id) to get all words in a specific article
        3. Use custom queries on the words table to get more detailed statistics
        """

    def search_word(self, word: str):
        # Database interaction comment:
        """
        To search for a word in the database:
        1. Use SearchWizard.search_articles_word(word) to find articles containing the word
        2. Use TextBuilder.build_context(self.title, word) to get the context of the word in this article
        """
        pass

    def get_word_index(self, word: str):
        # Database interaction comment:
        """
        To get the index of a word in the database:
        Use TextBuilder.build_words_index(word, self.title) to get the positions of the word in this article
        """
        pass


    def show(self):
        print(f'{self.title} by {self.author}')
        print(self.content)




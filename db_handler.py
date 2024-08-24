"""
This module handles database operations for the article processing system.
It provides a DB_handler class for managing connections and operations with a PostgreSQL database.
"""

import psycopg2


def parse_name(full_name):
    """
    Parse a full name into first name and last name.

    Args:
        full_name (str): The full name to parse.

    Returns:
        Tuple[str, str]: A tuple containing the first name and last name.
    """
    parts = full_name.split()
    if len(parts) == 1:
        return parts[0], ''
    first_name = parts[0]
    last_name = ' '.join(parts[1:])
    return first_name, last_name


class DBHandler:
    """
    Handles database operations for the article processing system.

    This class manages the connection to a PostgreSQL database and provides methods
    for creating schemas, tables, and performing various database operations.
    """

    def __init__(self):
        """
        Initialize the DB_handler and establish a connection to the database.
        """
        # Connect to the database. PLEASE MAKE SURE TO change the  credentials to the ones on your local server.
        self.connection = psycopg2.connect(dbname="db_project", user="omri", password="omri",
                                           options="-c search_path=text_handle")
        self.cursor = self.connection.cursor()

    def check_connection(self):
        """
        Check if the database connection is active.

        Returns:
            bool: True if the connection is active, False otherwise.
        """
        try:
            self.cursor.execute("SELECT 1")
            return True
        except psycopg2.Error as e:
            print(f"Connection error: {e}")
            return False

    def create_schemas(self):
        """Create the necessary schemas in the database."""
        self.cursor.execute(" CREATE SCHEMA IF NOT EXISTS art_info; ")
        self.connection.commit()
        self.cursor.execute(" CREATE SCHEMA IF NOT EXISTS text_handle; ")
        self.connection.commit()

    def create_types(self):
        """Create custom types used in the database."""
        self.cursor.execute("""
                        DO $$ BEGIN
                            CREATE TYPE position_type AS ( paragraph_number INTEGER, line_number INTEGER, 
                            position_in_line INTEGER, finishing_chars varchar(10), starting_chars varchar(10));
                        EXCEPTION
                            WHEN duplicate_object THEN null;
                        END $$;
                        DO $$ BEGIN
                            CREATE TYPE occurrence_type AS ( article_id INTEGER, positions position_type[] );
                        EXCEPTION
                            WHEN duplicate_object THEN null;
                        END $$;
                         """)
        self.connection.commit()

    def create_tables(self):
        """Create all required tables in the database."""
        self.cursor.execute(" CREATE TABLE IF NOT EXISTS art_info.Newspapers(np_id UUID PRIMARY KEY, np_name TEXT) ")
        self.connection.commit()
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS art_info.Articles( article_id SERIAL PRIMARY KEY,  
                            article_title TEXT, date DATE ,reporter_id INT, np_id UUID,
                            CONSTRAINT articles_fk FOREIGN KEY (np_id)
                            REFERENCES art_info.Newspapers (np_id));
                            """)
        self.connection.commit()
        self.cursor.execute(
            " CREATE TABLE IF NOT EXISTS  art_info.reporters(reporter_id SERIAL PRIMARY KEY, "
            " first_name TEXT, last_name TEXT) ")
        self.connection.commit()
        self.cursor.execute(""" CREATE TABLE IF NOT EXISTS text_handle.words ( word_id SERIAL PRIMARY KEY, 
                                word TEXT, occurrences occurrence_type[]); """)
        self.connection.commit()
        self.cursor.execute(""" CREATE TABLE IF NOT EXISTS text_handle.word_groups(group_id SERIAL PRIMARY KEY, 
                             group_description TEXT, word_ids INTEGER[]); """)
        self.connection.commit()
        self.cursor.execute(
            " CREATE TABLE IF NOT EXISTS text_handle.phrases(phrase_id SERIAL PRIMARY KEY, phrase TEXT )")
        self.connection.commit()

    def create_triggers(self):
        """Create database triggers for data integrity and validation."""
        # Create a trigger that checks whether an article is already in the table or not.
        self.cursor.execute(" CREATE OR REPLACE FUNCTION art_info.check_article_exists() "
                            " RETURNS TRIGGER AS $$ "
                            " BEGIN "
                                " IF EXISTS (SELECT a.article_id "
                                "            FROM art_info.articles a JOIN art_info.newspapers n "
                                "            ON a.np_id = n.np_id"
                                "            WHERE a.article_title = NEW.article_title AND a.date = NEW.date) THEN "
                                "   RAISE EXCEPTION 'The phrase % is too long', NEW.article_title; "
                                "   RETURN NULL; "
                                "ELSE "
                                "   RETURN NEW; "
                                "END IF; "
                            " END; "
                            " $$ LANGUAGE plpgsql; "
                            " CREATE OR REPLACE TRIGGER article_insert_update_trigger "
                            " BEFORE INSERT ON art_info.articles "
                            " FOR EACH ROW EXECUTE FUNCTION art_info.check_article_exists(); ")
        self.connection.commit()
        # Create a trigger that checks if a newspaper already exists to prevent duplications.
        self.cursor.execute(" CREATE OR REPLACE FUNCTION art_info.check_np_exists() "
                            " RETURNS TRIGGER AS $$ "
                            " BEGIN "
                            " IF EXISTS (SELECT np_id "
                            "            FROM art_info.newspapers "
                            "            WHERE np_name = NEW.np_name) THEN"
                            "   RETURN NULL; "
                            "ELSE "
                            "   RETURN NEW; "
                            "END IF; "
                            " END; "
                            " $$ LANGUAGE plpgsql; "
                            " CREATE OR REPLACE TRIGGER np_insert_trigger "
                            " BEFORE INSERT ON art_info.newspapers "
                            " FOR EACH ROW EXECUTE FUNCTION art_info.check_np_exists(); ")
        self.connection.commit()
        # Create a trigger that checks if a reporter already exists to prevent duplications.
        self.cursor.execute(" CREATE OR REPLACE FUNCTION art_info.check_reporter_exists() "
                            " RETURNS TRIGGER AS $$ "
                            " BEGIN "
                            " IF EXISTS (SELECT reporter_id "
                            "            FROM art_info.reporters "
                            "            WHERE first_name = NEW.first_name AND last_name = NEW.last_name ) THEN "
                            "   RETURN NULL; "
                            "ELSE "
                            "   RETURN NEW; "
                            "END IF; "
                            " END; "
                            " $$ LANGUAGE plpgsql; "
                            " CREATE OR REPLACE TRIGGER reporter_insert_trigger "
                            " BEFORE INSERT ON art_info.reporters "
                            " FOR EACH ROW EXECUTE FUNCTION art_info.check_reporter_exists(); ")
        self.connection.commit()
        # Create a trigger that checks if a phrase already exists to prevent duplications.
        self.cursor.execute("""
                            CREATE OR REPLACE FUNCTION text_handle.check_phrase_exists()
                            RETURNS TRIGGER AS $$
                            BEGIN
                                IF EXISTS (
                                    SELECT 1
                                    FROM text_handle.phrases
                                    WHERE phrase = NEW.phrase
                                ) THEN
                                    RAISE EXCEPTION 'Phrase "%s" already exists.', NEW.phrase;
                                ELSE
                                    RETURN NEW;
                                END IF;
                            END;
                            $$ LANGUAGE plpgsql;
                            CREATE OR REPLACE TRIGGER phrase_insert_trigger
                            BEFORE INSERT ON text_handle.phrases
                            FOR EACH ROW EXECUTE FUNCTION text_handle.check_phrase_exists();
        """)
        self.connection.commit()
        # Create a trigger that checks if a phrase is ascii or not.
        # This is also used to check whether the phrase is in English or not.
        self.cursor.execute("""
                            CREATE OR REPLACE FUNCTION check_ascii_string() 
                            RETURNS trigger AS $$
                            BEGIN
                                IF NEW.phrase !~ '^[\\x00-\\x7F]*$' THEN
                                    RAISE EXCEPTION 'The phrase contains non-ASCII characters: %', NEW.phrase;
                                ELSE
                                    RETURN NEW;
                                END IF;
                            END;
                            $$ LANGUAGE plpgsql;                         
                            CREATE OR REPLACE TRIGGER ascii_check_trigger
                            BEFORE INSERT OR UPDATE ON text_handle.phrases
                            FOR EACH ROW
                            EXECUTE FUNCTION check_ascii_string();
        """)
        self.connection.commit()
        # Create a trigger that checks if a phrase is longer than 100 characters or not.
        self.cursor.execute("""
                            CREATE OR REPLACE FUNCTION check_string_length() 
                            RETURNS trigger AS $$
                            BEGIN
                                IF LENGTH(NEW.phrase) > 100 THEN
                                    RAISE EXCEPTION 'The phrase % is too long', NEW.phrase;
                                ELSE
                                    RETURN NEW;
                                END IF;
                            END;
                            $$ LANGUAGE plpgsql;                         
                            CREATE OR REPLACE TRIGGER check_length_trigger
                            BEFORE INSERT OR UPDATE ON text_handle.phrases
                            FOR EACH ROW
                            EXECUTE FUNCTION check_string_length();
        """)
        self.connection.commit()

    def create_view(self):
        """Create a view for convenient word position querying."""
        self.cursor.execute("""
                            CREATE OR REPLACE VIEW text_handle.words_positions AS 
                                SELECT 
                                    w.word_id as word_id,
                                    w.word as word,
                                    o.article_id as article_id,
                                    pos.paragraph_number as paragraph_number,
                                    pos.line_number as line_number,
                                    pos.position_in_line as position_in_line,
                                    pos.starting_chars as starting_chars,
                                    pos.finishing_chars as finishing_chars
                                FROM 
                                    text_handle.words w,
                                    unnest(w.occurrences) as o(article_id, positions),
                                    unnest(o.positions) as pos(paragraph_number, line_number, 
                                    position_in_line, starting_chars, finishing_chars);                     
                                    """)
        self.connection.commit()

    # Getters:

    # Get reporter_id from reporter's name:
    def get_reporter_id_from_name(self, reporter_full_name):
        """
        Get the reporter ID(s) from the reporter's full name.

        Args:
            reporter_full_name (str): The full name of the reporter.

        Returns:
            List[Tuple[Any, ...]]: A list of tuples containing reporter ID(s).
        """
        first_name, last_name = parse_name(reporter_full_name)
        self.cursor.execute(" SELECT reporter_id "
                            " FROM art_info.reporters "
                            " WHERE LOWER(first_name)=LOWER(%s) AND LOWER(last_name) = lower(%s) ",
                            (first_name, last_name))
        self.connection.commit()
        return self.cursor.fetchall()

    # Get np_id from np_name
    # The assumption is that there are no 2 newspapers with the same name.
    def get_np_id_from_name(self, np_name):
        """
        Get the newspaper ID from the newspaper name.

        Args:
            np_name (str): The name of the newspaper.

        Returns:
            List[Tuple[Any, ...]]: A list of tuples containing newspaper ID(s).
        """
        self.cursor.execute(" SELECT np_id "
                            " FROM art_info.Newspapers "
                            " WHERE np_name = %s ",
                            (np_name,))
        self.connection.commit()
        return self.cursor.fetchall()

    def get_word_id_from_word(self, word):
        """
        Get the word ID for a given word.

        Args:
            word (str): The word to look up.

        Returns:
            int: The word ID if found, -1 otherwise.
        """
        self.cursor.execute(" SELECT word_id "
                            " FROM text_handle.words "
                            " WHERE word = %s ",
                            (word,))
        self.connection.commit()
        res = self.cursor.fetchall()
        if len(res) == 0:
            return -1
        else:
            return res[0][0]

    def get_article_id_from_title(self, article_title):
        """
        Get the article ID from the article title.

        Args:
            article_title (str): The title of the article.

        Returns:
            List[Tuple[Any, ...]]: A list of tuples containing article ID(s).
        """
        self.cursor.execute(" SELECT article_id "
                            " FROM art_info.articles "
                            " WHERE article_title = %s ",
                            (article_title,))
        self.connection.commit()
        return self.cursor.fetchall()

    def get_all_article_titles(self):
        """
        Get all article titles from the database.

        Returns:
            List[Tuple[str]]: A list of tuples, each containing an article title.
        """
        self.cursor.execute(" SELECT article_title FROM art_info.articles ")
        self.connection.commit()
        return self.cursor.fetchall()

    def get_total_articles(self):
        """
        Get the total number of articles in the database.

        Returns:
            int: The total number of articles.
        """
        self.cursor.execute("SELECT COUNT(*) FROM art_info.articles")
        self.connection.commit()
        return self.cursor.fetchone()[0]

    def get_all_articles(self):
        """
        Get all articles from the database.

        Returns:
            List[Tuple[Any, ...]]: A list of tuples containing articles.
        """
        self.cursor.execute(""" SELECT ROW_NUMBER() OVER (ORDER BY a.article_title) AS row_number, 
                                        n.np_name, a.article_title, a.date 
                                FROM art_info.articles a JOIN art_info.newspapers n
                                ON a.np_id = n.np_id
                                 ORDER BY row_number, n.np_name, a.date""")
        self.connection.commit()
        return self.cursor.fetchall()

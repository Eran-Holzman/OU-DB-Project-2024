import psycopg2


def parse_name(full_name):
    # Split the full name by spaces
    parts = full_name.split()

    # Handle cases with no spaces (single name)
    if len(parts) == 1:
        return parts[0], ''

    # Handle cases with more than one space (more than two names)
    first_name = parts[0]
    last_name = ' '.join(parts[1:])

    return first_name, last_name


class DB_handler:
    def __init__(self):
        # Connect to the database. PLEASE MAKE SURE TO change the  credentials to the ones on your local server.
        self.connection = psycopg2.connect(dbname="db_project", user="omri", password="omri",
                                           options="-c search_path=text_handle")
        self.cursor = self.connection.cursor()

    def create_schemas(self):
        self.cursor.execute(" CREATE SCHEMA IF NOT EXISTS art_info; ")
        self.connection.commit()
        self.cursor.execute(" CREATE SCHEMA IF NOT EXISTS text_handle; ")
        self.connection.commit()

    def create_types(self):
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

        # Function to create all the required tables:

    # Magazines, Volumes, Articles, Reporters,
    # As part of the creation of the articles table, a new type is created to store the article's pages
    def create_tables(self):
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
        self.cursor.execute(" CREATE TABLE IF NOT EXISTS text_handle.phrases(phrase_id SERIAL PRIMARY KEY, phrase TEXT )")
        self.connection.commit()

    def create_triggers(self):
    # Create a trigger that checks whether an article is already in the table or not.
        self.cursor.execute(" CREATE OR REPLACE FUNCTION art_info.check_article_exists() "
                            " RETURNS TRIGGER AS $$ "
                            " BEGIN "
                                " IF EXISTS (SELECT a.article_id "
                                "            FROM art_info.articles a JOIN art_info.newspapers n "
                                "            ON a.np_id = n.np_id"
                                "            WHERE a.article_title = NEW.article_title AND a.date = NEW.date) THEN"
                                "   RAISE NOTICE 'The article % exists already.', NEW.article_title; "
                                "   RETURN NULL; "
                                "ELSE "
                                "   RETURN NEW; "
                                "END IF; "
                            " END; "
                            " $$ LANGUAGE plpgsql; "
                            " CREATE OR REPLACE TRIGGER article_insert_update_trigger "
                            " BEFORE INSERT ON art_info.articles "
                            "FOR EACH ROW EXECUTE FUNCTION art_info.check_article_exists(); ")
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

    # Getters:

    # Get reporter_id from reporter's name:
    def get_reporter_id_from_name(self, reporter_full_name):
        first_name, last_name = parse_name(reporter_full_name)
        self.cursor.execute(" SELECT reporter_id "
                            " FROM art_info.reporters "
                            " WHERE LOWER(first_name)=LOWER(%s) AND LOWER(last_name) = lower(%s) ",
                            (first_name, last_name))
        return self.cursor.fetchall()

    # Get np_id from np_name
    # The assumption is that there are no 2 newspapers with the same name.
    def get_np_id_from_name(self, np_name):
        self.cursor.execute(" SELECT np_id "
                            " FROM art_info.Newspapers "
                            " WHERE np_name = %s ",
                            (np_name,))
        return self.cursor.fetchall()

    def get_word_id_from_word(self, word):
        self.cursor.execute(" SELECT word_id "
                            " FROM text_handle.words "
                            " WHERE word = %s ",
                            (word,))
        res = self.cursor.fetchall()
        if len(res) == 0:
            return -1
        else:
            return res[0][0]

    def get_article_id_from_title(self, article_title):
        self.cursor.execute(" SELECT article_id "
                            " FROM art_info.articles "
                            " WHERE article_title = %s ",
                            (article_title,))
        return self.cursor.fetchall()

    def get_all_article_titles(self):
        self.cursor.execute(" SELECT article_title FROM art_info.articles ")
        return self.cursor.fetchall()





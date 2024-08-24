from db_handler import *
from streamlitUI import StreamlitUI


class Main:
    """
     Main class that orchestrates the application's components.

     This class initializes the database handler and the Streamlit UI,
     and provides methods to set up the database and run the application.

     Attributes:
         database (DB_handler): An instance of the database handler.
         ui (StreamlitUI): An instance of the Streamlit user interface.
     """

    def __init__(self):
        """
           Initialize the Main class.

           Creates instances of the DB_handler and StreamlitUI classes.
           """
        self.database = DBHandler()
        self.ui = StreamlitUI()

    def init_db(self):
        """
        Initialize the database.

        This method sets up the database by creating necessary schemas,
        custom types, tables, triggers, and views.
        """
        self.database.create_schemas()
        self.database.create_types()
        self.database.create_tables()
        self.database.create_triggers()
        self.database.create_view()

    def run(self):
        """
        Run the application.

        This method starts the Streamlit user interface.
        """
        self.ui.run()


if __name__ == "__main__":
    app = Main()
    app.init_db()
    app.run()

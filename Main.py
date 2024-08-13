from DB_handler import *
from StreamlitUI import StreamlitUI

class Main:
    def __init__(self):
        self.database = DB_handler()
        self.ui = StreamlitUI(self.database)

    def init_db(self):
        self.database.create_schemas()
        self.database.create_types()
        self.database.create_tables()
        self.database.create_triggers()
        self.database.create_view()

    def run(self):
        self.ui.run()



if __name__ == "__main__":
    app = Main()
    app.init_db()
    app.run()

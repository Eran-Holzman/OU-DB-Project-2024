# Dynamic PostgreSQL Database Management for Text Analysis

This project demonstrates a Python-based integration with a PostgreSQL database to manage and analyze textual data, specifically news articles. It includes functionality for article management, reporter information, newspaper details, word position tracking, and full-text search.

## **Features**
- **Dynamic Schema and Table Creation**: Automates the setup of database schemas, tables, and custom data types.
- **Database Features**:
  - Word position tracking (paragraph, line, position).
  - Article metadata storage.
  - Efficient full-text search capabilities.
- **Text Analysis**: 
  - Word position tracking.
  - Context retrieval.
  - Article reconstruction.
  - Phrase and word group management.

## **Modules**
- `DBHandler`: A Python class to manage database operations like creating schemas, tables, types, and triggers.
- **Functions and Utilities**:
  - `parse_name`: A utility to parse full names into first and last names.
  - Getter methods to retrieve specific database IDs based on names.

## **Setup and Installation**
1. **Database Requirements**:
   - PostgreSQL must be installed and running on your local machine.

2. **Python Requirements**:
   - Python 3.10.9
   - Install dependencies using:
     ```bash
     pip install psycopg2 streamlit
     ```

## **Database Schema Overview**
### **Schemas:**
- **`info_art`**: Stores article, reporter, and newspaper information.
- **`handle_text`**: Handles text analysis data, including words, phrases, and word groups.

### **Key Tables in `info_art` Schema:**
- `Newspapers`: Stores newspaper data (np_id, np_name).
- `Articles`: Stores article data (article_id, article_title, date, reporter_id).
- `Reporters`: Stores reporter information (reporter_id, first_name, last_name).

### **Key Tables in `handle_text` Schema:**
- `Words`: Stores words appearing in articles (word_id, word, occurrences).
- `Words_group`: Stores custom word groups (group_id, group_description, words).
- `Phrases`: Stores custom phrases (phrase_id, phrase).

## **Tech Stack**
- **Programming Language**: Python
- **Database**: PostgreSQL
- **Libraries**: psycopg2, Streamlit
- **UI**: Streamlit

## **User Interface (UI) Overview**
The user interface is built using Python's Streamlit library. It includes:
- A dropdown menu for selecting categories.
- A free-text search field.
- Displaying results in pop-up windows when searching for specific data (e.g., context of a word).
- A short description of the website's purpose and usage instructions.

### **User Interaction Flow**:
- The user selects an option from the dropdown menu.
- Based on the selection, the following options are presented:
  1. Free text search.
  2. Additional menu options for more refined searches or actions.

## **Database Structure**
- **Schemas**:
  - `info_art`: Contains metadata about articles.
  - `handle_text`: Contains text data and analysis.
  
### **Tables in `info_art`**:
- **Newspapers**: Stores information about newspapers.
- **Articles**: Stores article-specific information.
- **Reporters**: Stores data about reporters.

### **Tables in `handle_text`**:
- **Words**: Stores each word's occurrences across articles.
- **Words_group**: Manages custom word groups.
- **Phrases**: Manages custom phrases.

## **Database Functions and Features**:
- **Document Loading**: The program loads articles into the database, storing newspaper, article, and reporter data.
- **Text Analysis Functions**:
  - Display all words in an article.
    <img src="https://i.imgur.com/qUHYs8X.png" alt="Homepage" width="300" style="margin-bottom: 10px;"/>

  - Display context for a word (one line above and below the word in the article).
  - Search for a word's index.
  - Identify words by their position.
  - Define custom word groups and phrases.
  - Display index for custom word groups or phrases.
  - Display statistics for articles based on words and phrases.



**Run the Script:**
   - Execute the script to run the site locally:
     ```
     python -m streamlit run main.py
     ```


## **Contributors**
- **Eran Holzman & Omri Beck**

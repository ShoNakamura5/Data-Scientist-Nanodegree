# import libraries
import pandas as pd
from sqlalchemy import create_engine
import sqlite3
import sys


def load_data(messages_filepath, categories_filepath):
    """
    INPUT
    df - messages dataset, categories dataset
    
    OUTPUT
    df - A data frame that classifies categories and is merged with data of the same id.
    1. Load datasets.
    2. Merged with data of the same id.
    3.Classifies categories.
    """
    
    # load messages dataset
    messages = pd.read_csv(messages_filepath)
    # load categories dataset
    categories = pd.read_csv(categories_filepath)
    # merge datasets
    df = messages.merge(categories, on=['id'])
    # create a dataframe of the 36 individual category columns
    categories = df['categories'].str.split(";", expand=True)
    # select the first row of the categories dataframe
    row = categories.head(1)
    # use this row to extract a list of new column names for categories.
    category_colnames = row.applymap(lambda x: x[:-2]).iloc[0, :].tolist()
    # rename the columns of `categories`
    categories.columns = category_colnames
    
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].astype(str).str[-1]
        # convert column from string to numeric
        categories[column] = categories[column].astype(int)
    
    # drop the original categories column from `df`
    df.drop('categories', axis=1, inplace=True)

    # concatenate the original dataframe with the new `categories` dataframe
    df = pd.concat([df, categories], axis=1)
    
    return df

def clean_data(df):
    """
    INPUT
    df - Data frame created by def load_data.
    
    OUTPUT
    df - Data frame with duplicated data and related=2 data removed.
    """
    # drop duplicates
    df.drop_duplicates(inplace=True)
    
    #　Remove related=2
    df = df[df.related != 2]
    return df


def save_data(df, database_filepath):
    engine = create_engine('sqlite:///'+ str (database_filepath))
    df.to_sql('Response', engine, index=False, if_exists = 'replace')

def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()
import pandas as pd
import requests
import json
from datetime import date, timedelta
import time
import sqlite3

# Scrape relevant articles and store
NEWS_API = '7c0e73b941f9483bb57f879cf9f551b9'
URL = 'https://newsapi.org/v2/everything'

def get_articles(keyword):
    # TODO: Try to scrape as many articles as possible from different sources
    params = {
        'q': keyword,
        'pageSize': 100,
        'apiKey': NEWS_API,
        'language': 'en',
        'from': date.today() - timedelta(days=30),
        'sources': 'bbc-news'
    }

    request_response = requests.get(URL, params = params)
    response_json = request_response.json()

    articles = response_json['articles']
    
    df = pd.DataFrame(articles)
    df = df[['title', 'author', 'description', 'url', 'publishedAt', 'content']]

    # Replace content column with scraped full text
    content = get_content(df['url'])
    df['content'] = content
    return df

def get_content(URLs):
    # TODO: get full text from URL (refer to scrape_bbc_articles.py)
    return URLs

def store_to_db(df):
    # Connect to 'data.db', a database I created for the demo. You would want to connect to our main database, init.db
    conn = sqlite3.connect('data.db')

    # Store dataframe in database
    # Right now, we replace the database with the new dataframe
    df.to_sql('article', conn, if_exists='replace', index=False)

    # Commit and close the connection
    conn.commit()
    conn.close()
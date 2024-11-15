import pandas as pd
import requests
import json
from datetime import date, timedelta
import time
import sqlite3
import xmltodict
import requests
import json
import sys
sys.path.append("..")
import scrape_bbc_articles

# Scrape relevant articles and store
NEWS_API = '7c0e73b941f9483bb57f879cf9f551b9'
URL = 'https://newsapi.org/v2/everything'

# # Colors for printing debugging text
# RED = '\033[91m'
# GREEN = '\033[92m'
# ENDC = '\033[0m'
# BLUE = '\033[94m'
# ua = UserAgent()
# HEADERS = {'User-Agent': ua.random}

def get_articles_using_newsapi(keyword):
    """
    Searches for BBC articles that related to "keyword" topics, 
    scrapes their content, and returns a dataframe with these articles
    "keyword" must be a string that satisfies the requirements at:
    (see https://newsapi.org/docs/endpoints/everythinghttps://newsapi.org/docs/endpoints/everything )
    """
    # TODO: Try to scrape as many articles as possible from different sources
    # This function is using NewsAPI, which isn't working
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
    print(response_json)

    articles = response_json['articles']
    df = pd.DataFrame(articles)
    print("Num of articles found: ",len(df))
    print(df.head())
    
    df = df[['title', 'author', 'description', 'url', 'publishedAt', 'content']]

    # Replace content column with scraped full text
    df['content'] = [" ".join(visit_link(URL)) for URL in df['url']]
    return df

def get_articles_using_rss(keyword):
    """
    Searches for BBC articles that related to "keyword" topics, 
    scrapes their content, and returns a dataframe with these articles
    """
    
    def getRSS(url: str) -> dict:
        response = requests.get(url)
        return xmltodict.parse(response.content)

    def saveRSS(filepath: str, data: dict) -> None:
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)
    
    data = getRSS("https://feeds.bbci.co.uk/news/business/rss.xml")

    saveRSS("database\\rss_feed_0.json", data)

    # now read the news from the saved file
    with open("database\\rss_feed_0.json", 'r') as file:
        data = json.load(file)
        num_articles = len(data['rss']['channel']['item'])
        print(f"Number of articles from RSS: {num_articles}")

        for item in data['rss']['channel']['item']:
            print(item['title'])
            print(item['description'])
            print(item['link'])
            print()

        topic = "AI"  # Replace with your topic
        filtered_urls = [item['link'] for item in data['rss']['channel']['item'] if topic.lower() in item['title'].lower() or topic.lower() in item['description'].lower()]
        print(filtered_urls)
        print(f"Number of relevant URLS: {len(filtered_urls)}")

    # Prepare data for DataFrame
    articles = [
        {
            'title': item.get('title'),
            'description': item.get('description'),
            'url': item.get('link'),
            'publishedAt': item.get('pubDate')
        }
        for item in data['rss']['channel']['item']
    ]

    df = pd.DataFrame(articles)
    print("Num of articles found: ",len(df))
    print(df.head())
    
    df = df[['title', 'description', 'url', 'publishedAt']]
    print(df['title'])

    # Replace content column with scraped full text
    content = get_content(df['url'])
    df['content'] = content
    return df

def get_sample_articles():
    """
    Returns a fixed dataframe with bbc article contents for testing
    """
    scrape_bbc_articles.scrape_samples() #generates csv file bbc_articles.csv
    df = pd.read_csv("Articles/bbc_articles.csv")
    return df

# def store_to_db(df):
#     # Connect to 'data.db', a database I created for the demo. You would want to connect to our main database, init.db
#     conn = sqlite3.connect('data.db')

#     # Store dataframe in database
#     df.to_sql('article', conn, if_exists='replace', index=False)
#     # print("Successfully stored in database!")
#     # Commit and close the connection
#     conn.commit()
#     conn.close()

def store_to_db(df):
    # Connect to 'data.db', a database I created for the demo. You would want to connect to our main database, init.db
    conn = sqlite3.connect('data.db')

    # Check number of rows before the operation
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='article'")
    table_exists = cursor.fetchone()[0]

    if table_exists:
        cursor.execute("SELECT COUNT(*) FROM article")
        rows_before = cursor.fetchone()[0]
    else:
        rows_before = 0

    print(f"Number of rows before: {rows_before}")

    # Store DataFrame in database
    df.to_sql('article', conn, if_exists='replace', index=False)

    # Check number of rows after the operation
    cursor.execute("SELECT COUNT(*) FROM article")
    rows_after = cursor.fetchone()[0]

    print(f"Number of rows after: {rows_after}")

    # Commit and close the connection
    conn.commit()
    conn.close()
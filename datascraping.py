import pandas as pd
import sqlite3
from datetime import date, timedelta
import requests
import json
import time
import random
from bs4 import BeautifulSoup

# Scrape relevant articles and store
NEWS_API = '7c0e73b941f9483bb57f879cf9f551b9'
URL = 'https://newsapi.org/v2/everything'

def get_articles_using_newsapi(keyword):
    params = {
        'q': keyword,
        'pageSize': 100,
        'apiKey': NEWS_API,
        'language': 'en',
        'from': date.today() - timedelta(days=30)
    }

    request_response = requests.get(URL, params = params)
    response_json = request_response.json()
    response_articles = response_json['articles']
    json_object = json.dumps(response_articles)

    with open("articles.json", "w") as outfile:
        outfile.write(json_object)

def process_articles():
    with open('articles.json', 'r') as f:
        articles_json = json.load(f)

    df = pd.DataFrame(articles_json)
    df = df[['title', 'url', 'content']]

    df['content'] = get_contents(df['url'])
    df = df.explode("content", ignore_index=True)
    df.dropna(inplace=True)
    df.to_csv('articles.csv')

    store_to_db(df)
    # print(df.head())

def store_to_db(df):
    # Connect to 'data.db'
    df.dropna(inplace=True)

    conn = sqlite3.connect('data.db')

    cursor = conn.cursor()
    table = """ CREATE TABLE IF NOT EXISTS paragraphs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            URL TEXT NOT NULL,
            content TEXT UNIQUE NOT NULL
        ); """
    cursor.execute(table)
    insert_sql = """INSERT OR REPLACE INTO paragraphs (title, url, content)
    VALUES (?, ?, ?)
    """
    for _, row in df.iterrows():
        cursor.execute(insert_sql, (row['title'], row['url'], row['content']))

    conn.commit()
    conn.close()

def make_request(URL, max_retries = 10, base_delay = 0.2, backoff_factor = 2):
    retries = 0

    while retries < max_retries:
        time.sleep(base_delay)
        response = requests.get(URL, headers = {'User-Agent': 'Mpzilla/5.0 AppleWebKit/537.36'})

        if response.status_code == 429:
            delay = base_delay * (backoff_factor ** retries)
            jitter = random.uniform(0, delay)
            delay_with_jitter = delay + jitter
            print("Got a 429 error. Retrying after {delay_with_jitter:.2f} seconds")
            time.sleep(delay_with_jitter)
            retries += 1
        else:
            print("Able to visit URL!")
            return response
        
    return response
            
def get_contents(URLs):
    content = []
    for URL in URLs:
        response = make_request(URL)
        if response is None or response.status_code != 200:
            content.append(None)
            continue

        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        # Multiple extraction methods for robustness
        text_blocks = []
        
        # Try specific div with data-component
        specific_blocks = [p.get_text(strip=True) for div in soup.find_all("div", {"data-component": "text-block"}) for p in div.find_all("p")]
        
        # Fallback to main content areas
        if not specific_blocks:
            content_divs = soup.find_all(["div", "article"], class_=["content", "main-text", "article-body"])
            paragraphs = [p.get_text(strip=True) for div in content_divs for p in div.find_all("p")]
        else:
            paragraphs = specific_blocks

        content.append(paragraphs)

    return content

def retrieve_data():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT content FROM articles')
    result = cursor.fetchall()
    content = [row[0] for row in result]
    # id = [row[0] for row in result]
    # content = [row[1] for row in result]

    conn.close()

    return content
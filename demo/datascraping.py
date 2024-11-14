import pandas as pd
import requests
import json
from datetime import date, timedelta
import time
import sqlite3
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random

# Scrape relevant articles and store
NEWS_API = '7c0e73b941f9483bb57f879cf9f551b9'
URL = 'https://newsapi.org/v2/everything'

# Colors for printing debugging text
RED = '\033[91m'
GREEN = '\033[92m'
ENDC = '\033[0m'
BLUE = '\033[94m'
ua = UserAgent()
HEADERS = {'User-Agent': ua.random}

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
    df['content'] = [" ".join(visit_link(URL)) for URL in df['url']]
    return df

def make_request(URL, max_retries = 10, base_delay = 0.2, backoff_factor = 2):
    retries = 0
    while retries < max_retries:
        time.sleep(base_delay)
        response = requests.get(URL, headers=HEADERS)
        if response.status_code == 429:  # Too many requests error
            #Calculate delay using exponential backoff
            delay = base_delay * (backoff_factor ** retries)
            jitter = random.uniform(0, delay)
            delay_with_jitter = delay + jitter
            # print(f"Got a 429 error. Retrying after {delay_with_jitter:.2f} seconds.")
            time.sleep(delay_with_jitter)
            retries += 1
        elif response.status_code == 200:
            # print("Able to visit URL!")
            return response
        else:
            # print(f"{RED}{response.status_code} error. Not able to visit {url}{ENDC}")
            return response
    raise Exception(f"Max retries exceeded for {URL}")

def visit_link(URL):
    response = make_request(URL)
    if response is None or response.status_code != 200:
        # print(f"{RED}Error {response.status_code}. Not able to access {URL}{ENDC}")
        return
    
    # Parse the HTML content
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    # print(f"Downloading article text from article: {BLUE}{URL}{ENDC}.")

    text_blocks = [p.get_text() for div in soup.find_all("div", {"data-component": "text-block"}) for p in div.find_all("p")]

    return text_blocks


def store_to_db(df):
    # Connect to 'data.db', a database I created for the demo. You would want to connect to our main database, init.db
    conn = sqlite3.connect('data.db')

    # Store dataframe in database
    df.to_sql('article', conn, if_exists='append', index=False)

    # Commit and close the connection
    conn.commit()
    conn.close()
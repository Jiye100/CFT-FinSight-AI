import pandas as pd
import requests
import json
from datetime import date, timedelta
import time

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

def get_content(URLs):
    for URL in URLs:
        scrape_bbc_articles.visit_link(URL)
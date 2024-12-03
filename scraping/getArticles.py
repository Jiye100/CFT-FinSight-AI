import requests
import pandas as pd
from datetime import datetime, timedelta

#My API Key
API_KEY = ''
URL = 'https://newsapi.org/v2/everything'


today = datetime.now()
#They only let me get articles from 1 month ago on the free plan
oneMonth = today - timedelta(days=30)

params = {
    'apiKey': API_KEY,
    'sources': 'bbc-news',
    'q': 'markets OR business OR finance OR economy OR stocks OR economic policy OR rates OR bonds OR crypto OR federal reserver OR IPO OR company OR fintech OR currency',
    'language': 'en',
    'pageSize': 100,
    'from': oneMonth.strftime('%Y-%m-%d'),
    'to': today.strftime('%Y-%m-%d'),
    'sortBy': 'publishedAt',
    'page': 1
}

articlesList = []

def getArticles(page):
    params['page'] = page
    response = requests.get(URL, params)
    data = response.json()
    
    if data['status'] != 'ok':
        print(f"Error : {data.get('message')}")
        return
    
    return data['articles']

def processArticles():
    print(f"Processing Articles")
    articles = getArticles(1)
    articlesList.extend(articles)

    print(f"Total number of articles: {len(articlesList)}")

    df = pd.DataFrame(articlesList)
    df = df[['source', 'author', 'title', 'description', 'url', 'publishedAt', 'content']]
    df['source_id'] = df['source'].apply(lambda x: x.get('id'))
    df['source_name'] = df['source'].apply(lambda x: x.get('name'))
    df.drop('source', axis=1, inplace=True)
    df.to_csv('articles.csv', index=False)
    print("Articles saved to 'articles.csv'")

processArticles()
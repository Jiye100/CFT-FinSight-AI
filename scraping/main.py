import requests
import csv

url = ('https://newsapi.org/v2/everything?'
       'q=-"The latest five minute news bulletin from BBC World Service.",finance OR inflation OR interest rates OR economy OR stock market OR investments OR loans OR debt OR credit OR risk management OR derivatives OR bonds OR mutual funds OR cryptocurrency OR fiscal policy OR monetary policy OR unemployment OR tax policy OR liquidity OR asset management OR capital markets OR forex OR commodities OR trade deficit OR gdp OR recession OR bankruptcy OR pensions&'
       'sources=bbc-news&'
       'from=2024-09-23&'
       'to=2024-10-22&'
       'sortBy=popularity&'
       'pageSize=100&'
       'apiKey=66652eff48894102a4d3dd225287ec18')

data = requests.get(url).json()

with open(input("CSV file name: "), mode='w', newline='', encoding='utf-8') as csv_file:
    fieldnames = ['source_id', 'source_name', 'author', 'title', 'description', 'url', 'urlToImage', 'publishedAt', 'content']

    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()

    for article in data['articles']:
        source_id = article['source']['id']
        source_name = article['source']['name']

        row = {
            'source_id': source_id,
            'source_name': source_name,
            'author': article.get('author'),
            'title': article.get('title'),
            'description': article.get('description'),
            'url': article.get('url'),
            'urlToImage': article.get('urlToImage'),
            'publishedAt': article.get('publishedAt'),
            'content': article.get('content')
        }
        writer.writerow(row)


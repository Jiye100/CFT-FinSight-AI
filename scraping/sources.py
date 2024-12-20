import requests
import csv

url = ('https://newsapi.org/v2/top-headlines/sources?'
      'language=en&'
      'apiKey')
      

data = requests.get(url).json()

with open(input("CSV file name: "), mode='w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(data['sources'][0].keys())
    for source in data['sources']:
        writer.writerow(source.values())

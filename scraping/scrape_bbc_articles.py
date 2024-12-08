# import libraries
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import pandas as pd
import random

##After running this program the resulting file structure will look like:

#colors for printing debugging text
RED = '\033[91m'
GREEN = '\033[92m'
ENDC = '\033[0m'
BLUE = '\033[94m'
ua = UserAgent()
HEADERS = {'User-Agent': ua.random}


#Function to return the response of a webpage request, and retrying after some time if getting 429 errors
def make_request(url, max_retries=10, base_delay=0.2, backoff_factor=2, verbose=True):
    retries = 0
    while retries < max_retries:
        time.sleep(base_delay)
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 429:  # Too many requests error
            #Calculate delay using exponential backoff
            delay = base_delay * (backoff_factor ** retries)
            jitter = random.uniform(0, delay)
            delay_with_jitter = delay + jitter
            print(f"Got a 429 error. Retrying after {delay_with_jitter:.2f} seconds.")
            time.sleep(delay_with_jitter)
            retries += 1
        elif response.status_code == 200:
            #print("Able to visit URL!")
            return response
        else:
            print(f"{RED}{response.status_code} error. Not able to visit {url}{ENDC}")
            return response
    raise Exception(f"Max retries exceeded for {url}")

def visit_link(URL):
    """
    Visits the URL link, parses the text, and returns a new 
    row for the article
    """
    response = make_request(URL, verbose=False)
    if response is None or response.status_code != 200:
        print(f"{RED}Error {response.status_code}. Not able to access {URL}{ENDC}")
        return

    # Parse the HTML content
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    #print(f"Downloading article text from article: {BLUE}{URL}{ENDC}.")
    new_row = {} #new row for the article that will be added to df

    text_blocks = [p.get_text() for div in soup.find_all("div", attrs={"data-component": "text-block"}) for p in div.find_all("p")]
    #print(text_blocks)
 
    
    new_row["Source"] = "BBC"
    new_row["URL"] = URL
    title_block = soup.find('div', {'data-component': 'headline-block'})
    title_tag = soup.find('h1', id='main-heading')
    #print("Printing the tag",title_tag)
    title = title_tag.text if title_tag else None
    # print(soup.find("article"))
    #print(title)
    #title = title_block.find('h1').text if title_block else None
    new_row["Title"] =  title
    subheadline_blocks = soup.find_all('div', {'data-component': 'subheadline-block'})
    subheadlines = [block.find('h2').text for block in subheadline_blocks if block.find('h2')]
    new_row["Headlines"] = subheadlines
    new_row["Text Body"] = text_blocks

    #convert our new row from a dictionary to a dataframe
    new_row_df = pd.DataFrame([new_row])
    return new_row_df

    
    # k=10
    # #Write saved articles to csv after scraping every k articles
    # if len(df)%k==0:
    #     print(f"{GREEN}Writing progress to csv.{ENDC}")
    #     df.to_csv(f"Articles/bbc_articles.csv")
    df.to_csv(f"Articles/bbc_articles.csv")

def scrape_samples():
    """
    Creates a csv file Articles/sample_bbc_articles.csv containing the full content of a 
    few articles, for RAG testing purposes
    """
    print("Scraping articles...")
    #These BBC news article URLS are from articles.csv
    bbc_urls = [
        "https://www.bbc.co.uk/news/articles/c5yrl1vgne9o",
        "https://www.bbc.co.uk/news/articles/cje03dq2pyyo",
        "https://www.bbc.co.uk/news/articles/c0j8w73pdn8o",
        "https://www.bbc.co.uk/news/articles/c704wzx38p1o",
        "https://www.bbc.co.uk/news/articles/cvglmv4lgx0o",
        "https://www.bbc.co.uk/news/articles/cvg745ggn3no",
        "https://www.bbc.co.uk/news/articles/cpvzypy8ndyo"
    ]

    df = pd.DataFrame(columns=["Source","URL", "Title", "Headlines", "Text Body"])
    for url in bbc_urls:
        new_article_row = visit_link(url) #scrape the url and create a row for that article
        if new_article_row is None:
            print(f"{RED}Error getting content from {url}{ENDC}")
            continue
        #print(new_article_row.columns)
        new_article_row = new_article_row[df.columns]
        #print(new_article_row.columns)
        df = pd.concat([df, new_article_row], ignore_index=True) #add that article to our dataframe
    df.to_csv(f"Articles/sample_bbc_articles.csv", index=False)
    #print(df.columns)
    #print("Saved BBC articles csv to Articles/sample_bbc_articles.csv.")

def scrape_articles(bbc_urls):
    """
    Creates a csv file Articles/bbc_articles.csv containing the full content of a 
    few articles, for RAG testing purposes

    Input: urls: a list of BBC news article URLs to scrape
    Output: Creates the file Articles/bbc_articles.csv containing scraped text bodies
    """
    #print("Scraping articles...")

    df = pd.DataFrame(columns=["Source","URL", "Title", "Headlines", "Text Body"])
    for url in bbc_urls:
        new_article_row = visit_link(url) #scrape the url and create a row for that article
        if new_article_row is None:
            print(f"{RED}Error getting content from {url}{ENDC}")
            continue
        #print(new_article_row.columns)
        new_article_row = new_article_row[df.columns]
        #print(new_article_row.columns)
        df = pd.concat([df, new_article_row], ignore_index=True) #add that article to our dataframe
    df.to_csv(f"Articles/bbc_articles.csv", index=False)
    #print(df.columns)
    #print("Saved BBC articles csv to Articles/bbc_articles.csv.")


if __name__ == "__main__":
    scrape_samples()
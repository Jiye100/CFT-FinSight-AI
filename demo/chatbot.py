# import google.generativeai as genai
# import os
# import datascraping
# import sys
# sys.path.append("..")
# import config #containing the API key
# import langchain
# from langchain.sql_database import SQLDatabase
# from langchain_community.utilities.sql_database import SQLDatabase
# from langchain_experimental.sql import SQLDatabaseChain

# # Get Gemini API key#
# # os.environ["GEMINI_API_KEY"] = config.GEMINI_API_KEY # Put your personal API key
# # genai.configure(api_key=os.environ["GEMINI_API_KEY"])
# # model = genai.GenerativeModel('gemini-pro')

# os.environ["GEMINI_API_KEY"] = config.GEMINI_API_KEY # Put your personal API key
# genai.configure(api_key=os.environ["GEMINI_API_KEY"])
# model = genai.GenerativeModel("gemini-1.5-flash")

# prompt = input("What can I help with?\n") #user enters a query
# # TODO: revise prompt to output keywords

# response = model.generate_content(prompt)
# print(response.text)

# # Create a chat session
# #chat = model.start_chat(history=[])

# # prompt = input("What can I help with?\n") #user enters a query
# # # TODO: revise prompt to output keywords

# #TODO: Add to the prompt, asking the LLM to get keywords from the user's query

# #response = chat.send_message(prompt, stream=True)
# # TODO: get list of keywords from the response

# # print(response.text)
# keyword = 'inflation OR economy' # sample keyword

# df = datascraping.get_articles(keyword)
# datascraping.store_to_db(df)

# #now relevant data to the query is stored in data.db (or init.db)

# # Load the SQL database
# db = SQLDatabase.from_uri("sqlite:///data.db")
# # Load data
# #loader = langchain.SQLDatabaseLoader(db, table_name="your_table_name")
# #docs = loader.load()
# db_chain = SQLDatabaseChain.from_llm(llm=model, db=db, verbose=True,
#                                      return_intermediate_steps=True, top_k=1)
# result = db_chain(prompt) 
# print(result)

import google.generativeai as genai
import datascraping
import sys
sys.path.append("..")
from config import GEMINI_API_KEY #containing the API key

import pandas as pd

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

user_query = input("What can I help with?\n") #user enters a query
#response = model.generate_content(f"Here is a client's finance-related question: {user_query}. What are some main topics I could filter by to search for relevant news articles?")
#print(response)
#print("Converting response to dict...")
#data = response.to_dict() #converts the response to dictionary python
#response_text = data['candidates'][0]['content']['parts'][0]['text']
#print(response_text)
#TODO: revise prompt to output keywords that satisfy the formatting requirements
keyword = 'semiconductor OR microchip' # sample keyword
#df = datascraping.get_articles_using_rss(keyword)

df = datascraping.get_sample_articles()
print("Loaded the articles dataframe!")
print(df.head())
datascraping.store_to_db(df)
print("Stored the dataframe in the db.")


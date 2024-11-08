import google.generativeai as genai
import os
import datascraping

# Get Gemini API key
os.environ["GEMINI_API_KEY"] = 'GEMINI_API_KEY' # Put your personal API key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

# Create a chat session
chat = model.start_chat(history=[])

prompt = input("What can I help with?\n")
# TODO: revise prompt to output keywords

response = chat.send_message(prompt, stream=True)
# TODO: get list of keywords from the response

keyword = 'inflation OR economy' # sample keyword

df = datascraping.get_articles(keyword)
datascraping.store_to_db(df)
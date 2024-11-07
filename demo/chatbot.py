import google.generativeai as genai
import os
import datascraping

# Get Gemini API key
os.environ["GEMINI_API_KEY"] = 'YOUR_API_KEY'
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

# Create a chat session
chat = model.start_chat(history=[])

prompt = input("What can I help with?\n")
# TODO: revise prompt to output keywords

response = chat.send_message(prompt, stream=True)
# TODO: get list of keywords from the response

keyword = 'real estate OR investment OR mortgage rate' # sample keyword

datascraping.get_articles(keyword)
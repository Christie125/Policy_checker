import link_scraper
from openrouter import OpenRouter
import os

content = link_scraper.scrape_links()

prompt = "You are a summariser app for security conscious people trying to understand the legal terms of their website. Summarise the following content, highlighting potential security concerns. Do not make anything up. Here is the content:" + " ".join(content)

proccessed_content = []

client = OpenRouter(
    api_key=os.getenv("API_KEY"),
    server_url="https://ai.hackclub.com/proxy/v1",
)

response = client.chat.send(
    model="google/gemini-3.7-flash",
    messages=[
       {"role": "user", "content": prompt}
    ],
    stream=True,
)

# Print chunks as they arrive from the server
for chunk in response:
    if chunk.choices and chunk.choices[0].delta.content:
        text_chunk = chunk.choices[0].delta.content
        proccessed_content.append(text_chunk)

def format_output(proccessed_content):
    proccessed_content = "".join(proccessed_content)
    print("Processed content:", proccessed_content)
    return proccessed_content
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import cohere
from twilio.rest import Client

# Formate date for url
def get_formatted_date():
    current_date = datetime.now()
    formatted_date = current_date.strftime("%B-%-d-%Y").lower()
    return formatted_date

# Get environment variables
cohere_api_key = 'abVbU5puEUTBnsGQq8hPXnAeH9JtGvH9pIstM5z9'
twilio_account_sid = 'AC550489d0cf20897e81015e172989a7e9'
twilio_auth_token = '3da2be03d8a2d2259fb7f800b44d7b4d'
to_phone_number = '+14049155010'
twilio_sender_phone_number = '+18778425481'

# News and markets urls alongside cohere key for summarization
url = "https://theweek.com/digest/round-up/10-things-you-need-to-know-today-"+get_formatted_date()
markets_url = "https://www.edwardjones.com/us-en/market-news-insights/stock-market-news/daily-market-recap"
co = cohere.Client(cohere_api_key)

# getting the article text for summarization using beautiful soup and requests for scraping and parsing
def get_article_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    article_body = soup.find('div', {'id': 'article-body', 'class': 'article__body'})
    result_text = ""

    if article_body:
        ptags = article_body.find_all('p')  

        for p in ptags:
            paragraph_text = p.text.strip()
            if len(paragraph_text) > 150:
                h3 = p.find_previous('h3')
                if h3:
                    result_text += h3.text.strip() + "\n" 
                    result_text += paragraph_text + "\n\n"  
    else:
        result_text = "No article body found."
    return result_text

# getting the markets text for summarization using beautiful soup and requests for scraping and parsing
def get_markets_text(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        section = soup.find('section', class_='w-full')

        if section:
            section_contents = section.get_text()
            scraped = section_contents
        else:
            scraped = "Section with class 'w-full' not found on the page."
    else:
        scraped = f"HTTP Error {response.status_code}"

    return scraped

markets_text = get_markets_text(markets_url)
article_text = get_article_text(url)

# text summarization function using cohere api
def cohere_summarizer(co, text):
    try:
        response = co.summarize(
            text=text,
            length='Medium',
            format='bullets',
            model='command',
            additional_command='Provide a summary of the text in easy to understand bullet points',
            temperature=0.4
        )
        summary = response.summary
        return summary
    except:
        return "No news today, something's wrong"

article_summary = cohere_summarizer(co, article_text)
markets_summary = cohere_summarizer(co, markets_text)

# finally building the full text message using both summaries and some personal touches
def string_builder(article, markets):
    formatted_date = get_formatted_date()

    # Define emojis
    sun_emoji = "☀️"
    bed_emoji = "🛏️"
    water_emoji = "💧"
    skincare_emoji = "🧴"
    news_emoji = "📰"
    money_emoji = "💰"
    creatine_emoji = "💊"

    final_string = f"""Good Morning {sun_emoji}!

{bed_emoji} Make bed
{creatine_emoji} Creatine
{water_emoji} Water plants
{skincare_emoji} Skincare routine

{news_emoji} In the News:

{article}

{money_emoji} In Markets:

{markets}
"""
    return final_string

built_string = string_builder(article_summary, markets_summary)

# Check if built_string exceeds a character limit
character_limit = 1600
while len(built_string) > character_limit:
    
    markets_text = get_markets_text(markets_url)
    article_text = get_article_text(url)
    
    article_summary = cohere_summarizer(co, article_text)
    markets_summary = cohere_summarizer(co, markets_text)
    
    built_string = string_builder(article_summary, markets_summary)

# Initialize Twilio client
client = Client(twilio_account_sid, twilio_auth_token)

# Send the message
message = client.messages.create(
    from_=twilio_sender_phone_number,
    body=built_string,
    to=to_phone_number
)
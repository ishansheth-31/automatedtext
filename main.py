import subprocess
import datetime
import json
import requests
from bs4 import BeautifulSoup
import cohere

bed_emoji = "🛏️"
creatine_emoji = "💊"
water_emoji = "💧"
skincare_emoji = "🧖‍♂️"
news_emoji = "📰"
market_emoji = "💹"


url = "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZxYUdjU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen"
markets = "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB/sections/CAQiXENCQVNQd29JTDIwdk1EbHpNV1lTQW1WdUdnSlZVeUlQQ0FRYUN3b0pMMjB2TURsNU5IQnRLaG9LR0FvVVRVRlNTMFZVVTE5VFJVTlVTVTlPWDA1QlRVVWdBU2dBKioIAComCAoiIENCQVNFZ29JTDIwdk1EbHpNV1lTQW1WdUdnSlZVeWdBUAFQAQ?hl=en-US&gl=US&ceid=US%3Aen"

def scrape_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        page_title = soup.title.string
        page_text = soup.get_text()
        scraped = page_text
    else:
        scraped = response.status_code
    return scraped

cnbc_scraped = scrape_page(url)
markets_scraped = scrape_page(markets)


co = cohere.Client('abVbU5puEUTBnsGQq8hPXnAeH9JtGvH9pIstM5z9')
response = co.summarize( 
  text = cnbc_scraped,
  length='long',
  format='bullets',
  model='command-nightly',
  additional_command='give me a 4-5 bullet daily summary of the news and make it go in depth',
  temperature=0.3
) 
summary = response.summary

markets_summary = co.summarize( 
  text = markets_scraped,
  length='long',
  format='bullets',
  model='command-nightly',
  additional_command='give me a 4-5 bullet daily summary of the news and make it go in depth',
  temperature=0.3
) 
market_summarizer = markets_summary.summary

def get_formatted_date():

    current_date = datetime.date.today()
    day_name = current_date.strftime('%A')
    month_name = current_date.strftime('%B')
    day_number = current_date.day
    formatted_date = f'{day_name}, {month_name}, {day_number}'

    return formatted_date





formatted_date = get_formatted_date()
phone = "14049155010"
body = f"""Good Morning! Today is {formatted_date}. 😃 Remember to do the following:

{bed_emoji} Make your bed.
{creatine_emoji} Take your creatine.
{water_emoji} Water your plants.
{skincare_emoji} Do your skincare routine.

In Today's News {news_emoji}:

{summary}

In the Markets {market_emoji}:

{market_summarizer}
"""





payload = {
    "from": "12085810221",
    "to": [phone],
    "body": body
}

payload_json = json.dumps(payload)

# Define the curl command as a list of strings
curl_command = [
    'curl',
    '-X', 'POST',
    '-H', 'Authorization: Bearer 0477a9ff18af4fe7adb0ba863f7cd3a7',
    '-H', 'Content-Type: application/json',
    '-d', payload_json,  # Use the JSON string here
    'https://sms.api.sinch.com/xms/v1/cf1175f4cbec488fa113ee4956c73b9e/batches'
]

try:
    result = subprocess.run(curl_command, capture_output=True, text=True, check=True)
    print("Curl command output:")
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print("Curl command failed with an error:")
    print(e.stderr)

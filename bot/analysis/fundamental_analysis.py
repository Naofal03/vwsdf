import requests

def fetch_news(api_key):
    url = f"https://newsapi.org/v2/everything?q=forex&apiKey={api_key}"
    response = requests.get(url)
    return response.json()

def analyze_news(news_data):
    sentiments = []
    for article in news_data['articles']:
        sentiment = analyze_sentiment(article['title'])
        sentiments.append(sentiment)
    return sum(sentiments) / len(sentiments)

def analyze_sentiment(text):
    return 1 if "positive" in text.lower() else -1
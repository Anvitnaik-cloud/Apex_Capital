import os
import requests
import feedparser
import streamlit as st


@st.cache_data(ttl=900)
def fetch_news(ticker, max_items=8):
    api_key = os.getenv("NEWSAPI_KEY", "")
    if api_key:
        url = (
            "https://newsapi.org/v2/everything"
            f"?q={ticker}&sortBy=publishedAt&pageSize={max_items}&apiKey={api_key}"
        )
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            articles = []
            for item in data.get("articles", []):
                articles.append(
                    {
                        "title": item.get("title"),
                        "source": item.get("source", {}).get("name"),
                        "url": item.get("url"),
                        "published": item.get("publishedAt", ""),
                    }
                )
            return articles

    rss_url = f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries[:max_items]:
        articles.append(
            {
                "title": entry.get("title"),
                "source": entry.get("source", {}).get("title", "Google News"),
                "url": entry.get("link"),
                "published": entry.get("published", ""),
            }
        )
    return articles

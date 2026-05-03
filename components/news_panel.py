import streamlit as st

from utils.news import fetch_news
from utils.sentiment import score_sentiment


def render_news_panel(ticker, asset_type):
    st.subheader("Latest Market News")
    with st.spinner("Fetching headlines..."):
        articles = fetch_news(ticker)

    if not articles:
        st.info("No news articles found. Try another ticker or set NEWSAPI_KEY.")
        return

    for article in articles:
        sentiment = score_sentiment(article.get("title", ""))
        st.markdown(f"**{article.get('title', 'Headline')}**")
        st.caption(f"{article.get('source', 'Source')} | {article.get('published', '')} | Sentiment: {sentiment}")
        if article.get("url"):
            st.markdown(f"[Read article]({article['url']})")
        st.divider()

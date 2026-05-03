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
        title = article.get("title", "Headline")
        source = article.get("source", "Source")
        published = article.get("published", "")
        url = article.get("url", "")

        link_html = f"<a href='{url}' target='_blank' style='color:#7B61FF; text-decoration:none;'>Read article</a>" if url else ""

        st.markdown(
            f"""
            <div class="news-card">
                <div class="news-title">{title}</div>
                <div class="news-meta">{source} | {published} | Sentiment: {sentiment}</div>
                {link_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

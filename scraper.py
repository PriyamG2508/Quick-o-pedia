import requests
from bs4 import BeautifulSoup
import re
import streamlit as st

@st.cache_data  

def scrape_wikipedia(topic):
    formatted_topic = topic.replace(' ', '_')
    wiki_url = f'https://en.wikipedia.org/wiki/{formatted_topic}'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        res = requests.get(wiki_url, headers=headers)
        if res.status_code == 404:
            print("Article not found. Try a different topic.")
            return None
            
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Extract text from paragraphs
        corpus = ''
        for p in soup.find_all('p'):
            corpus += p.get_text() + '\n'
        
        # Clean the text more efficiently
        corpus = re.sub(r'\[\d+\]', '', corpus)  # Remove citations
        corpus = re.sub(r'\n\s*\n', '\n\n', corpus)  # Clean spacing
        corpus = corpus.strip()
        
        return corpus
        
    except Exception as e:
        raise RuntimeError(f"Failed to scrape Wikipedia: {e}")

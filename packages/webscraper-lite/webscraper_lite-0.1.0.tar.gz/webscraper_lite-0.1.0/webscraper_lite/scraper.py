import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

def scrape_website(url):
    fall_back_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    try:
        # Add custom headers to look like a real browser
        headers = {
            "User-Agent": UserAgent(fallback= fall_back_ua).random,    
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        
        # Send GET request with headers
        response = requests.get(url, headers=headers, timeout=100)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract content
        text = soup.get_text(separator='\n', strip=True)        
        return text
    except Exception as e:
        return {"error": str(e)}




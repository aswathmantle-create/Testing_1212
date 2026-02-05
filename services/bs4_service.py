"""
Enhanced BeautifulSoup service for production-ready scraping.
Features: Rotating user agents, retry logic, better headers, cookie handling.
"""
import requests
from bs4 import BeautifulSoup
import html2text
import random
import time
from typing import Optional, Callable, Dict, Any
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from config.settings import REQUEST_TIMEOUT
from services.content_filter import clean_html_for_product

# Rotating User Agents to avoid detection
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]


class BS4Service:
    """Production-ready service for scraping URLs using BeautifulSoup."""
    
    def __init__(self, save_dir: str = None, max_retries: int = 3):
        self.save_dir = Path(save_dir) if save_dir else Path("mdfiles")
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.max_retries = max_retries
        self.session = requests.Session()
        
    def _get_headers(self, url: str) -> Dict[str, str]:
        """Generate realistic headers for the request."""
        parsed = urlparse(url)
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "Referer": f"{parsed.scheme}://{parsed.netloc}/",
        }

    def scrape_url(self, url: str, log_callback: Optional[Callable] = None) -> Dict[str, Any]:
        if log_callback:
            log_callback(f"🥣 BS4: Starting scrape for {url}")
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    wait_time = 2 ** attempt
                    if log_callback:
                        log_callback(f"   ⏳ Retry {attempt + 1}/{self.max_retries} after {wait_time}s...")
                    time.sleep(wait_time)
                
                headers = self._get_headers(url)
                
                response = self.session.get(
                    url, 
                    headers=headers, 
                    timeout=REQUEST_TIMEOUT,
                    allow_redirects=True
                )
                
                # Check for blocking responses
                if response.status_code == 403:
                    raise Exception("403 Forbidden - Site may be blocking requests")
                elif response.status_code == 429:
                    raise Exception("429 Too Many Requests - Rate limited")
                elif response.status_code == 503:
                    raise Exception("503 Service Unavailable - May need retry")
                
                response.raise_for_status()
                
                # Apply smart content filter to extract only product data
                raw_html = response.content.decode('utf-8', errors='ignore')
                cleaned_html = clean_html_for_product(raw_html)
                
                # Fallback: If filtering removed too much, use less aggressive approach
                if len(cleaned_html) < 500:  # Too little content retained
                    if log_callback:
                        log_callback(f"   ⚠️ Filtered content too small, using minimal filtering...")
                    soup = BeautifulSoup(raw_html, 'html.parser')
                    # Only remove the absolutely necessary noise
                    for element in soup(["script", "style", "noscript", "iframe"]):
                        element.decompose()
                    cleaned_html = str(soup)
                
                if log_callback:
                    log_callback(f"   🧹 Filtered HTML: {len(raw_html)} → {len(cleaned_html)} chars")

                h = html2text.HTML2Text()
                h.ignore_links = True  # Skip navigation links
                h.ignore_images = True  # Skip image tags (keep alt text)
                h.body_width = 0
                h.unicode_snob = True
                h.ignore_emphasis = False
                
                markdown_content = h.handle(cleaned_html)
                
                if log_callback:
                    log_callback(f"✅ BS4: Successfully scraped {len(markdown_content)} chars")
                    
                filename = self._save_markdown(url, markdown_content, log_callback)

                return {
                    "success": True,
                    "markdown": markdown_content,
                    "error": None,
                    "filename": filename
                }
                
            except requests.exceptions.Timeout:
                last_error = "Request timed out"
                if log_callback:
                    log_callback(f"   ⏱️ Timeout on attempt {attempt + 1}")
                    
            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {str(e)}"
                if log_callback:
                    log_callback(f"   🔌 Connection error on attempt {attempt + 1}")
                    
            except Exception as e:
                last_error = str(e)
                if log_callback:
                    log_callback(f"   ⚠️ Error on attempt {attempt + 1}: {last_error}")
        
        if log_callback:
            log_callback(f"❌ BS4: Failed after {self.max_retries} attempts - {last_error}")
            
        return {
            "success": False,
            "markdown": "",
            "error": last_error,
            "filename": ""
        }

    def _save_markdown(self, url: str, content: str, log_callback: Optional[Callable] = None) -> str:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace("www.", "").replace(".", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{domain}_{timestamp}_bs4.md"
            
            filepath = self.save_dir / filename
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# URL: {url}\n")
                f.write(f"# Method: BS4\n")
                f.write(f"# Scraped: {datetime.now().isoformat()}\n\n")
                f.write(content)
            
            if log_callback:
                log_callback(f"   📁 Saved to: mdfiles/{filename}")
            
            return filename
        except Exception as e:
            if log_callback:
                log_callback(f"   ⚠️ Could not save markdown: {str(e)}")
            return ""

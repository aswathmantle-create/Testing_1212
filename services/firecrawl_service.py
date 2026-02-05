"""
Firecrawl API service for scraping URLs to markdown.
"""
import requests
from typing import Optional, Callable
from pathlib import Path
from datetime import datetime
import re
from config.settings import FIRECRAWL_API_KEY, FIRECRAWL_API_URL, REQUEST_TIMEOUT, MAX_RETRIES


class FirecrawlService:
    """Service for scraping URLs using Firecrawl API."""
    
    def __init__(self, api_key: str = None, save_dir: str = None):
        self.api_key = api_key or FIRECRAWL_API_KEY
        self.base_url = FIRECRAWL_API_URL
        self.save_dir = Path(save_dir) if save_dir else Path("mdfiles")
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
    def _filter_markdown(self, markdown: str) -> str:
        """
        Filter markdown to remove non-product content.
        Removes sections like: related products, reviews, footer links, navigation.
        """
        lines = markdown.split('\n')
        filtered_lines = []
        skip_section = False
        
        # Patterns indicating noise sections (case-insensitive)
        noise_section_patterns = [
            r'^#+\s*(related|recommended|you may|also like|customers also|similar)',
            r'^#+\s*(reviews?|ratings?|customer feedback|testimonials)',
            r'^#+\s*(footer|navigation|menu|links)',
            r'^#+\s*(share|social|follow us)',
            r'^#+\s*(newsletter|subscribe|sign up)',
            r'^#+\s*(recently viewed|browsing history)',
            r'^#+\s*(compare|wishlist)',
        ]
        
        # Link-heavy line patterns (navigation/footer)
        noise_line_patterns = [
            r'^\s*[\*\-]\s*\[.*?\]\(.*?\)\s*$',  # Bullet point with just a link
            r'^\s*\|.*\|.*\|',  # Table rows with many pipes
        ]
        
        for line in lines:
            line_lower = line.lower()
            
            # Check if entering a noise section
            for pattern in noise_section_patterns:
                if re.match(pattern, line_lower):
                    skip_section = True
                    break
            
            # Check if this is a new heading (could exit noise section)
            if skip_section and re.match(r'^#+\s+', line):
                # Check if this heading indicates good content
                good_patterns = [
                    r'description', r'specification', r'feature', r'detail',
                    r'overview', r'about', r'highlight', r'what\'s in',
                    r'technical', r'dimension', r'warranty'
                ]
                for gp in good_patterns:
                    if gp in line_lower:
                        skip_section = False
                        break
            
            if skip_section:
                continue
            
            # Skip individual noisy lines
            is_noise_line = False
            for pattern in noise_line_patterns:
                if re.match(pattern, line):
                    is_noise_line = True
                    break
            
            # Skip lines that are just links or navigation
            if line.count('](') > 3:  # Too many links on one line
                continue
            
            if not is_noise_line:
                filtered_lines.append(line)
        
        # Remove excessive empty lines
        result = '\n'.join(filtered_lines)
        result = re.sub(r'\n{4,}', '\n\n\n', result)
        
        return result.strip()
    
    def scrape_url(self, url: str, log_callback: Optional[Callable] = None) -> dict:
        """
        Scrape a URL and convert to markdown.
        
        Args:
            url: The URL to scrape
            log_callback: Optional callback function for logging
            
        Returns:
            dict with 'success', 'markdown', and 'error' keys
        """
        if not self.api_key:
            return {
                "success": False,
                "markdown": "",
                "error": "Firecrawl API key not configured"
            }
            
        if log_callback:
            log_callback(f"🔥 Firecrawl: Starting scrape for {url}")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "url": url,
            "formats": ["markdown"]
        }
        
        for attempt in range(MAX_RETRIES):
            try:
                if log_callback:
                    log_callback(f"   Attempt {attempt + 1}/{MAX_RETRIES}...")
                    
                response = requests.post(
                    f"{self.base_url}/scrape",
                    headers=headers,
                    json=payload,
                    timeout=REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    raw_markdown = data.get("data", {}).get("markdown", "")
                    
                    # Apply markdown content filter
                    markdown_content = self._filter_markdown(raw_markdown)
                    
                    if log_callback:
                        log_callback(f"✅ Firecrawl: Successfully scraped {url}")
                        log_callback(f"   🧹 Filtered: {len(raw_markdown)} → {len(markdown_content)} chars")
                    
                    # Save markdown to file
                    filename = self._save_markdown(url, markdown_content, log_callback)
                        
                    return {
                        "success": True,
                        "markdown": markdown_content,
                        "error": None,
                        "filename": filename
                    }
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    if log_callback:
                        log_callback(f"⚠️ Firecrawl: Error - {error_msg}")
                        
                    if attempt == MAX_RETRIES - 1:
                        return {
                            "success": False,
                            "markdown": "",
                            "error": error_msg
                        }
                        
            except requests.exceptions.Timeout:
                if log_callback:
                    log_callback(f"⚠️ Firecrawl: Timeout on attempt {attempt + 1}")
                if attempt == MAX_RETRIES - 1:
                    return {
                        "success": False,
                        "markdown": "",
                        "error": "Request timeout"
                    }
                    
            except requests.exceptions.RequestException as e:
                if log_callback:
                    log_callback(f"⚠️ Firecrawl: Request error - {str(e)}")
                if attempt == MAX_RETRIES - 1:
                    return {
                        "success": False,
                        "markdown": "",
                        "error": str(e)
                    }
                    
        return {
            "success": False,
            "markdown": "",
            "error": "Max retries exceeded"
        }
    
    def _save_markdown(self, url: str, content: str, log_callback: Optional[Callable] = None) -> str:
        """
        Save markdown content to a file.
        
        Args:
            url: The source URL
            content: The markdown content
            log_callback: Optional logging function
            
        Returns:
            The filename where it was saved
        """
        try:
            # Generate filename from URL
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.replace("www.", "").replace(".", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{domain}_{timestamp}.md"
            
            filepath = self.save_dir / filename
            
            # Write markdown to file
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# URL: {url}\n")
                f.write(f"# Scraped: {datetime.now().isoformat()}\n\n")
                f.write(content)
            
            if log_callback:
                log_callback(f"   📁 Saved to: mdfiles/{filename}")
            
            return filename
        except Exception as e:
            if log_callback:
                log_callback(f"   ⚠️ Could not save markdown: {str(e)}")
            return ""
    
    def scrape_multiple_urls(self, urls: list, log_callback: Optional[Callable] = None) -> dict:
        """
        Scrape multiple URLs and return results.
        
        Args:
            urls: List of URLs to scrape
            log_callback: Optional callback function for logging
            
        Returns:
            dict mapping URL to result dict
        """
        results = {}
        
        for i, url in enumerate(urls):
            if url and url.strip():
                if log_callback:
                    log_callback(f"\n📄 Processing URL {i + 1}/{len(urls)}")
                results[f"url{i + 1}"] = self.scrape_url(url.strip(), log_callback)
            else:
                results[f"url{i + 1}"] = {
                    "success": False,
                    "markdown": "",
                    "error": "Empty URL"
                }
                
        return results

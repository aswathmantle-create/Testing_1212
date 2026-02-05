"""
Crawl4AI service for scraping URLs using AI-optimized crawler.
Updated to use proper SDK with BrowserConfig and CrawlerRunConfig.
Requires: pip install crawl4ai
"""
import asyncio
import nest_asyncio
from typing import Optional, Callable, Dict, Any
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from services.content_filter import clean_html_for_product
import html2text

# Apply nest_asyncio at module level for Streamlit compatibility
try:
    nest_asyncio.apply()
except:
    pass

# Check for Crawl4AI availability
CRAWL4AI_AVAILABLE = False
try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
    CRAWL4AI_AVAILABLE = True
except ImportError:
    AsyncWebCrawler = None
    BrowserConfig = None
    CrawlerRunConfig = None
    CacheMode = None


class Crawl4AIService:
    """Production-ready service for scraping using Crawl4AI."""
    
    def __init__(self, save_dir: str = None):
        self.save_dir = Path(save_dir) if save_dir else Path("mdfiles")
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
    def scrape_url(self, url: str, log_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Scrape a URL using Crawl4AI with proper configuration.
        """
        if not CRAWL4AI_AVAILABLE:
            error_msg = "Crawl4AI not installed. Run: pip install crawl4ai && crawl4ai-setup"
            if log_callback:
                log_callback(f"❌ {error_msg}")
            return {"success": False, "markdown": "", "error": error_msg, "filename": ""}

        if log_callback:
            log_callback(f"🕷️ Crawl4AI: Fetching {url}...")
            
        try:
            # Run the async crawl
            result = self._run_async_crawl(url, log_callback)
            
            if not result.success:
                error_msg = getattr(result, 'error_message', 'Unknown error')
                raise Exception(f"Crawl failed: {error_msg}")
            
            # Get markdown - handle both old and new API
            raw_markdown = ""
            if hasattr(result, 'markdown'):
                if hasattr(result.markdown, 'raw_markdown'):
                    raw_markdown = result.markdown.raw_markdown
                elif isinstance(result.markdown, str):
                    raw_markdown = result.markdown
            
            if not raw_markdown:
                raise Exception("No markdown content returned")
            
            # Apply content filter if HTML is available
            if hasattr(result, 'html') and result.html:
                cleaned_html = clean_html_for_product(result.html)
                
                # Fallback if filtering removed too much
                if len(cleaned_html) < 500:
                    if log_callback:
                        log_callback(f"   ⚠️ Filtered content too small, using raw markdown")
                    markdown = raw_markdown
                else:
                    h = html2text.HTML2Text()
                    h.ignore_links = True
                    h.ignore_images = True
                    h.body_width = 0
                    h.unicode_snob = True
                    markdown = h.handle(cleaned_html)
                    if log_callback:
                        log_callback(f"   🧹 Filtered: {len(result.html)} → {len(cleaned_html)} chars")
            else:
                markdown = raw_markdown
            
            if log_callback:
                log_callback(f"✅ Crawl4AI: Successfully scraped {len(markdown)} chars")
                
            filename = self._save_markdown(url, markdown, log_callback)
            
            return {
                "success": True,
                "markdown": markdown,
                "error": None,
                "filename": filename
            }
            
        except Exception as e:
            error_msg = str(e)
            if log_callback:
                log_callback(f"❌ Crawl4AI: Failed - {error_msg}")
            return {
                "success": False,
                "markdown": "",
                "error": error_msg,
                "filename": ""
            }

    def _run_async_crawl(self, url: str, log_callback: Optional[Callable] = None):
        """
        Run the async crawl in a sync context.
        Handles both running and non-running event loops.
        """
        async def _crawl():
            # Configure browser for stealth
            browser_config = BrowserConfig(
                headless=True,
                viewport_width=1920,
                viewport_height=1080,
                verbose=False
            )
            
            # Configure crawl run
            crawler_config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                remove_overlay_elements=True,  # Remove popups/modals
                wait_for_images=False,  # Faster loading
            )
            
            async with AsyncWebCrawler(config=browser_config) as crawler:
                if log_callback:
                    log_callback(f"   🌐 Browser launched, navigating...")
                result = await crawler.arun(url=url, config=crawler_config)
                return result
        
        # Handle event loop for Streamlit/sync context
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # nest_asyncio allows this
                return loop.run_until_complete(_crawl())
            else:
                return asyncio.run(_crawl())
        except RuntimeError:
            return asyncio.run(_crawl())

    def _save_markdown(self, url: str, content: str, log_callback: Optional[Callable] = None) -> str:
        """Save markdown content to file."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace("www.", "").replace(".", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{domain}_{timestamp}_c4ai.md"
            filepath = self.save_dir / filename
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# URL: {url}\n")
                f.write(f"# Scraped: {datetime.now().isoformat()}\n")
                f.write(f"# Method: Crawl4AI\n\n")
                f.write(content)
                
            if log_callback:
                log_callback(f"   📁 Saved to: mdfiles/{filename}")
            return filename
            
        except Exception as e:
            if log_callback:
                log_callback(f"   ⚠️ Could not save markdown: {str(e)}")
            return ""

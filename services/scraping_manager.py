from typing import Optional, Callable, Dict, Any
from services.bs4_service import BS4Service
from services.firecrawl_service import FirecrawlService

try:
    from services.crawl4ai_service import Crawl4AIService
except ImportError:
    Crawl4AIService = None

try:
    from services.playwright_service import PlaywrightService
except ImportError:
    PlaywrightService = None

class ScrapingManager:
    """
    Manager to handle different scraping strategies including Auto fallback.
    """
    
    def __init__(self):
        self.bs4_service = BS4Service()
        self.firecrawl_service = FirecrawlService()
        self.crawl4ai_service = Crawl4AIService() if Crawl4AIService else None
        self.playwright_service = PlaywrightService() if PlaywrightService else None
        
    def scrape_url(self, url: str, method: str = "Auto", log_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Scrape a URL using the specified method or Auto fallback.
        """
        # Normalize method
        method_key = method.strip()
        
        if log_callback:
            log_callback(f"🤖 Scraping Manager: Processing with {method_key}")
            
        if method_key == "BS4":
            return self.bs4_service.scrape_url(url, log_callback)
            
        elif method_key == "Crawl4AI":
            if self.crawl4ai_service:
                return self.crawl4ai_service.scrape_url(url, log_callback)
            return {"success": False, "markdown": "", "error": "Crawl4AI service not available", "filename": ""}
            
        elif method_key == "Playwright":
            if self.playwright_service:
                return self.playwright_service.scrape_url(url, log_callback)
            return {"success": False, "markdown": "", "error": "Playwright service not available", "filename": ""}
            
        elif method_key == "Firecrawl":
            return self.firecrawl_service.scrape_url(url, log_callback)
            
        elif method_key == "Auto":
            return self._scrape_auto(url, log_callback)
            
        else:
            return {"success": False, "markdown": "", "error": f"Unknown method: {method}", "filename": ""}
            
    def _scrape_auto(self, url: str, log_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Fallback logic: BS4 -> Crawl4AI -> Playwright -> Firecrawl
        """
        # 1. BS4
        if log_callback: log_callback("🔄 Auto: Trying BS4...")
        res = self.bs4_service.scrape_url(url, log_callback)
        if res["success"]: return res
        if log_callback: log_callback(f"   BS4 Failed: {res.get('error')}")
        
        # 2. Crawl4AI
        if self.crawl4ai_service:
            if log_callback: log_callback("🔄 Auto: Trying Crawl4AI...")
            res = self.crawl4ai_service.scrape_url(url, log_callback)
            if res["success"]: return res
            if log_callback: log_callback(f"   Crawl4AI Failed: {res.get('error')}")
        
        # 3. Playwright
        if self.playwright_service:
            if log_callback: log_callback("🔄 Auto: Trying Playwright...")
            res = self.playwright_service.scrape_url(url, log_callback)
            if res["success"]: return res
            if log_callback: log_callback(f"   Playwright Failed: {res.get('error')}")
            
        # 4. Firecrawl
        if log_callback: log_callback("🔄 Auto: Trying Firecrawl...")
        return self.firecrawl_service.scrape_url(url, log_callback)

"""
Enhanced Playwright service for production-ready scraping.
Uses headless browser for JavaScript-rendered pages.
Features: Stealth mode, realistic behavior, anti-detection, expand buttons.
"""
import random
import re
from typing import Optional, Callable, Dict, Any
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import html2text
from config.settings import REQUEST_TIMEOUT
from services.content_filter import clean_html_for_product

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

# Rotating User Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

# Common viewport sizes
VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1536, "height": 864},
    {"width": 1440, "height": 900},
]

# Selectors for expandable/load more buttons across popular sites
EXPAND_BUTTON_SELECTORS = [
    # Generic expand/show more patterns
    "[class*='expand']",
    "[class*='show-more']",
    "[class*='showmore']",
    "[class*='read-more']",
    "[class*='readmore']",
    "[class*='load-more']",
    "[class*='loadmore']",
    "[class*='see-more']",
    "[class*='seemore']",
    "[class*='view-more']",
    "[class*='viewmore']",
    "[aria-expanded='false']",
    "[data-action='expand']",
    "[data-toggle='collapse']",
    
    # Amazon-specific
    "#productDescription-expander",
    ".a-expander-prompt",
    ".a-expander-header",
    "#aplus-expander-content",
    "#feature-bullets-expander",
    ".a-declarative[data-action='a-expander-toggle']",
    "[data-csa-c-type='widget'][data-csa-c-content-id*='expander']",
    "#btfContent .a-expander-prompt",
    
    # Best Buy-specific
    ".show-more-button",
    "[class*='ShowMore']",
    
    # Walmart-specific
    "[data-testid='see-more-link']",
    ".see-more-link",
    
    # Target-specific
    "[data-test='detailsTab']",
    "[data-test='specificationsTab']",
    
    # General e-commerce patterns
    "button[class*='spec']",
    "button[class*='detail']",
    "button[class*='description']",
    ".accordion-toggle",
    ".collapsible-trigger",
    ".toggle-content",
    "[role='button'][aria-expanded='false']",
    
    # Tab selectors (to click on tabs that reveal content)
    "[role='tab'][aria-selected='false']",
    ".tab:not(.active)",
    ".nav-tab:not(.active)",
]

# Text patterns to identify expand buttons
EXPAND_BUTTON_TEXT_PATTERNS = [
    r"show\s*more",
    r"read\s*more",
    r"see\s*more",
    r"view\s*more",
    r"load\s*more",
    r"expand",
    r"see\s*all",
    r"view\s*all",
    r"more\s*details",
    r"full\s*description",
    r"show\s*details",
    r"specifications",
    r"tech\s*specs",
]


class PlaywrightService:
    """Production-ready service for scraping dynamic pages using Playwright."""
    
    def __init__(self, save_dir: str = None):
        self.save_dir = Path(save_dir) if save_dir else Path("mdfiles")
        self.save_dir.mkdir(parents=True, exist_ok=True)
    
    def _expand_all_content(self, page, log_callback: Optional[Callable] = None) -> int:
        """
        Click all expandable buttons to reveal hidden content.
        Returns the count of buttons clicked.
        """
        clicked_count = 0
        
        # Method 1: Click by selector patterns
        for selector in EXPAND_BUTTON_SELECTORS:
            try:
                elements = page.locator(selector).all()
                for element in elements[:10]:  # Limit to prevent infinite loops
                    try:
                        if element.is_visible():
                            element.click(timeout=2000)
                            clicked_count += 1
                            page.wait_for_timeout(300)  # Small delay after click
                    except:
                        pass
            except:
                pass
        
        # Method 2: Find buttons/links by text content
        for pattern in EXPAND_BUTTON_TEXT_PATTERNS:
            try:
                # Look for buttons with matching text
                buttons = page.locator(f"button:has-text(/{pattern}/i)").all()
                for btn in buttons[:5]:
                    try:
                        if btn.is_visible():
                            btn.click(timeout=2000)
                            clicked_count += 1
                            page.wait_for_timeout(300)
                    except:
                        pass
                
                # Look for links/spans with matching text
                links = page.locator(f"a:has-text(/{pattern}/i), span:has-text(/{pattern}/i)").all()
                for link in links[:5]:
                    try:
                        if link.is_visible():
                            link.click(timeout=2000)
                            clicked_count += 1
                            page.wait_for_timeout(300)
                    except:
                        pass
            except:
                pass
        
        # Method 3: Amazon-specific expansion
        try:
            # Click on "Read more" links in product description
            amazon_expanders = page.locator(".a-expander-prompt, #productDescription-expander-link").all()
            for exp in amazon_expanders:
                try:
                    if exp.is_visible():
                        exp.click(timeout=2000)
                        clicked_count += 1
                        page.wait_for_timeout(300)
                except:
                    pass
        except:
            pass
        
        if log_callback and clicked_count > 0:
            log_callback(f"   🔓 Expanded {clicked_count} hidden content sections")
        
        return clicked_count
    
    def _scroll_to_load_content(self, page, log_callback: Optional[Callable] = None):
        """Scroll through the page to trigger lazy loading."""
        try:
            # Get page height
            page_height = page.evaluate("document.body.scrollHeight")
            viewport_height = page.evaluate("window.innerHeight")
            
            # Scroll in steps
            current_position = 0
            scroll_step = viewport_height * 0.8
            
            while current_position < page_height:
                page.evaluate(f"window.scrollTo(0, {current_position})")
                page.wait_for_timeout(400)
                current_position += scroll_step
                
                # Update page height (might grow due to lazy loading)
                new_height = page.evaluate("document.body.scrollHeight")
                if new_height > page_height:
                    page_height = new_height
            
            # Scroll back to top
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(500)
            
            if log_callback:
                log_callback(f"   📜 Scrolled through page to load lazy content")
        except:
            pass
        
    def scrape_url(self, url: str, log_callback: Optional[Callable] = None) -> Dict[str, Any]:
        if not sync_playwright:
            return {"success": False, "markdown": "", "error": "Playwright not installed", "filename": ""}
            
        if log_callback:
            log_callback(f"🎭 Playwright: Fetching {url}...")
            
        try:
            with sync_playwright() as p:
                # Launch with anti-detection settings
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                    ]
                )
                
                # Create context with realistic settings
                viewport = random.choice(VIEWPORTS)
                context = browser.new_context(
                    user_agent=random.choice(USER_AGENTS),
                    viewport=viewport,
                    locale='en-US',
                    timezone_id='Asia/Dubai',
                    geolocation={'latitude': 25.2048, 'longitude': 55.2708},
                    permissions=['geolocation'],
                )
                
                page = context.new_page()
                
                # Override navigator.webdriver to avoid detection
                page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)
                
                # Navigate with retry logic
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=REQUEST_TIMEOUT * 1000)
                    # Wait for network to settle
                    page.wait_for_load_state("networkidle", timeout=15000)
                except:
                    # If networkidle times out, proceed anyway
                    pass
                
                # Step 1: Scroll to trigger lazy loading
                if log_callback:
                    log_callback("   🔄 Scrolling to load lazy content...")
                self._scroll_to_load_content(page, log_callback)
                
                # Step 2: Expand all expandable content
                if log_callback:
                    log_callback("   🔓 Expanding hidden content sections...")
                self._expand_all_content(page, log_callback)
                
                # Step 3: Wait a bit for expanded content to render
                page.wait_for_timeout(1000)
                
                raw_content = page.content()
                browser.close()
            
            # Apply smart content filter to extract only product data
            cleaned_html = clean_html_for_product(raw_content)
            
            # Fallback: If filtering removed too much, use less aggressive approach
            if len(cleaned_html) < 500:  # Too little content retained
                if log_callback:
                    log_callback(f"   ⚠️ Filtered content too small, using minimal filtering...")
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(raw_content, 'html.parser')
                # Only remove the absolutely necessary noise
                for element in soup(["script", "style", "noscript", "iframe"]):
                    element.decompose()
                cleaned_html = str(soup)
            
            if log_callback:
                log_callback(f"   🧹 Filtered HTML: {len(raw_content)} → {len(cleaned_html)} chars")
                
            h = html2text.HTML2Text()
            h.ignore_links = True  # Skip navigation links
            h.ignore_images = True  # Skip image tags
            h.ignore_emphasis = False
            h.body_width = 0
            h.unicode_snob = True
            h.skip_internal_links = True
            markdown = h.handle(cleaned_html)
            
            # Post-process markdown to remove unwanted patterns
            markdown = self._clean_markdown(markdown)
            
            if log_callback:
                log_callback(f"✅ Playwright: Successfully scraped {len(markdown)} chars")
                
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
                log_callback(f"❌ Playwright: Failed - {error_msg}")
            return {
                "success": False,
                "markdown": "",
                "error": error_msg,
                "filename": ""
            }
    
    def _clean_markdown(self, markdown: str) -> str:
        """Post-process markdown to remove noise patterns."""
        lines = markdown.split('\n')
        cleaned_lines = []
        
        # Patterns to skip
        skip_patterns = [
            r'^#{1,6}\s*(menu|navigation|footer|header|sign\s*in|log\s*in|cart|wishlist|account).*$',
            r'^\s*\|\s*\|\s*$',  # Empty table rows
            r'^[-=_]{10,}$',  # Long separators
            r'^\s*©.*$',  # Copyright lines
            r'^\s*all\s*rights\s*reserved.*$',
            r'^\s*privacy\s*policy.*$',
            r'^\s*terms\s*(of\s*service|&\s*conditions).*$',
            r'^\s*cookie\s*policy.*$',
            r'^\s*(subscribe|newsletter).*$',
            r'^\s*follow\s*us.*$',
            r'^\s*(facebook|twitter|instagram|youtube|linkedin|pinterest).*$',
            r'^\s*share\s*(this|on|via).*$',
            r'^skip\s*to\s*(main\s*)?content.*$',
            r'^\s*\*\s*$',  # Single asterisks
            r'^\s*loading\.{3,}$',
            r'^\s*please\s*wait.*$',
        ]
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Skip empty lines in sequences (keep max 2)
            if not line.strip():
                if cleaned_lines and cleaned_lines[-1].strip() == '':
                    continue
                cleaned_lines.append(line)
                continue
            
            # Check against skip patterns
            should_skip = False
            for pattern in skip_patterns:
                if re.match(pattern, line_lower, re.IGNORECASE):
                    should_skip = True
                    break
            
            if not should_skip:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    def _save_markdown(self, url: str, content: str, log_callback: Optional[Callable] = None) -> str:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace("www.", "").replace(".", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{domain}_{timestamp}_pw.md"
            filepath = self.save_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# URL: {url}\n")
                f.write(f"# Method: Playwright\n")
                f.write(f"# Scraped: {datetime.now().isoformat()}\n\n")
                f.write(content)
            if log_callback:
                log_callback(f"   📁 Saved to: mdfiles/{filename}")
            return filename
        except Exception as e:
            if log_callback:
                log_callback(f"   ⚠️ Could not save markdown: {str(e)}")
            return ""

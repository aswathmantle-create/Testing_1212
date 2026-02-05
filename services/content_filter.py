"""
Content filtering utility for extracting only relevant product data from PDP pages.
Removes headers, footers, navigation, related products, reviews, and other noise.
"""
from bs4 import BeautifulSoup, Tag
from typing import List, Set
import re

# Elements to always remove (navigation, noise, non-product content)
REMOVE_TAGS = [
    "script", "style", "noscript", "iframe", "svg", "canvas",
    "header", "footer", "nav", "aside", "menu", "menuitem",
    "form", "input", "button", "select", "textarea",
]

# CSS classes/IDs that indicate non-product content (common patterns)
NOISE_PATTERNS = [
    # Headers/Navigation
    r"header", r"navbar", r"nav-", r"navigation", r"top-bar", r"topbar",
    r"menu", r"mega-menu", r"dropdown", r"hamburger",
    
    # Footers
    r"footer", r"foot-", r"bottom-bar", r"bottombar", r"copyright",
    
    # Related/Recommended products
    r"related", r"recommend", r"similar", r"also-bought", r"also-viewed",
    r"you-may-like", r"customers-also", r"frequently-bought",
    r"carousel", r"slider", r"swiper", r"slick",
    
    # Reviews/Comments (we want specs, not reviews)
    r"review", r"rating", r"comment", r"feedback", r"testimonial",
    r"star-rating", r"user-review", r"customer-review",
    
    # Social/Share
    r"social", r"share", r"facebook", r"twitter", r"instagram", r"pinterest",
    r"whatsapp", r"telegram", r"linkedin",
    
    # Ads/Banners/Popups
    r"banner", r"promo", r"popup", r"modal", r"overlay", r"ad-",
    r"advertisement", r"sponsored", r"newsletter", r"subscribe",
    
    # Misc noise
    r"breadcrumb", r"pagination", r"pager", r"sidebar", r"widget",
    r"cookie", r"gdpr", r"consent", r"chat", r"support-chat",
    r"recently-viewed", r"wishlist", r"compare",
]

# Patterns that indicate PRODUCT content (keep these)
PRODUCT_PATTERNS = [
    r"product-title", r"product-name", r"product-info",
    r"product-description", r"product-detail", r"product-spec",
    r"specification", r"spec-table", r"tech-spec", r"features",
    r"description", r"overview", r"about-product", r"highlights",
    r"key-features", r"bullet", r"attribute", r"property",
    r"price", r"offer", r"discount", r"sku", r"model",
    r"dimensions", r"weight", r"capacity", r"warranty",
    r"pdp-", r"detail-page", r"main-content", r"product-content",
    # Amazon-specific patterns
    r"title", r"titleblock", r"dp-", r"detail", r"feature",
    r"a-section", r"a-row", r"a-box", r"atc-",  # Amazon UI classes
    r"availability", r"buybox", r"cart",
    # E-commerce generic patterns
    r"item-", r"sku-", r"prod-", r"specs", r"info",
]


def _matches_pattern(text: str, patterns: List[str]) -> bool:
    """Check if text matches any of the patterns."""
    if not text:
        return False
    text_lower = text.lower()
    for pattern in patterns:
        if re.search(pattern, text_lower):
            return True
    return False


def _is_noise_element(element: Tag) -> bool:
    """Check if an element is noise based on its attributes."""
    # Always preserve critical tags
    if element.name in ['h1', 'h2', 'h3', 'main', 'article']:
        return False
    
    # Check class attribute
    classes = element.get("class", [])
    if isinstance(classes, list):
        class_str = " ".join(classes)
    else:
        class_str = str(classes)
    
    if _matches_pattern(class_str, NOISE_PATTERNS):
        # But don't remove if it also matches product patterns
        if not _matches_pattern(class_str, PRODUCT_PATTERNS):
            return True
    
    # Check id attribute
    elem_id = element.get("id", "")
    if _matches_pattern(elem_id, NOISE_PATTERNS):
        if not _matches_pattern(elem_id, PRODUCT_PATTERNS):
            return True
    
    # Check data attributes
    for attr, value in element.attrs.items():
        if attr.startswith("data-"):
            if isinstance(value, str) and _matches_pattern(value, NOISE_PATTERNS):
                return True
    
    return False


def _is_product_element(element: Tag) -> bool:
    """Check if element likely contains product content."""
    classes = element.get("class", [])
    if isinstance(classes, list):
        class_str = " ".join(classes)
    else:
        class_str = str(classes)
    
    elem_id = element.get("id", "")
    
    return (_matches_pattern(class_str, PRODUCT_PATTERNS) or 
            _matches_pattern(elem_id, PRODUCT_PATTERNS))


def clean_html_for_product(html_content: str) -> str:
    """
    Clean HTML to extract only product-relevant content.
    
    Args:
        html_content: Raw HTML string
        
    Returns:
        Cleaned HTML with only product-relevant content
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Step 1: Remove always-unwanted tags
    for tag in REMOVE_TAGS:
        for element in soup.find_all(tag):
            element.decompose()
    
    # Step 2: Remove elements matching noise patterns
    # ONLY remove if it's clearly noise AND doesn't contain product info
    elements_to_remove = []
    
    for element in soup.find_all(True):  # All tags
        if isinstance(element, Tag) and _is_noise_element(element):
            # Check element text content - if substantial, keep it
            text_content = element.get_text(strip=True)
            if len(text_content) > 100:  # Substantial content, probably important
                continue
            
            # Don't remove if it's a product element or contains product elements
            if not _is_product_element(element):
                has_product_child = any(
                    _is_product_element(child) 
                    for child in element.find_all(True)
                    if isinstance(child, Tag)
                )
                if not has_product_child:
                    elements_to_remove.append(element)
    
    for element in elements_to_remove:
        try:
            element.decompose()
        except:
            pass
    
    # Step 3: Remove empty elements
    for element in soup.find_all(True):
        if isinstance(element, Tag):
            text = element.get_text(strip=True)
            if not text and not element.find_all(['img', 'table']):
                try:
                    element.decompose()
                except:
                    pass
    
    # Step 4: Try to find main product container
    product_containers = []
    for element in soup.find_all(True):
        if isinstance(element, Tag) and _is_product_element(element):
            product_containers.append(element)
    
    # If we found clear product containers, use those
    if product_containers:
        # Get the largest one (most content)
        main_container = max(product_containers, key=lambda e: len(e.get_text()))
        return str(main_container)
    
    # Otherwise return cleaned body
    body = soup.find('body')
    if body:
        return str(body)
    
    return str(soup)


def extract_product_text(html_content: str) -> str:
    """
    Extract only product-relevant text from HTML.
    Returns clean text suitable for LLM processing.
    """
    cleaned_html = clean_html_for_product(html_content)
    soup = BeautifulSoup(cleaned_html, 'html.parser')
    
    # Get text with some structure preserved
    lines = []
    
    # Extract title - prioritize h1, then h2
    title_tags = soup.find_all(['h1'])
    if not title_tags:
        title_tags = soup.find_all(['h2'])
    for tag in title_tags[:3]:  # First 3 headings to catch product title
        text = tag.get_text(strip=True)
        if text and len(text) > 5 and len(text) < 500:  # Reasonable title length
            lines.append(f"# {text}")
    
    # Extract lists (bullet points, features)
    for ul in soup.find_all(['ul', 'ol']):
        for li in ul.find_all('li'):
            text = li.get_text(strip=True)
            if text and len(text) > 3:
                lines.append(f"• {text}")
    
    # Extract tables (specifications)
    for table in soup.find_all('table'):
        for row in table.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                if key and value:
                    lines.append(f"{key}: {value}")
    
    # Extract description paragraphs
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        if text and len(text) > 20:  # Skip very short paragraphs
            lines.append(text)
    
    # Extract definition lists (common for specs)
    for dl in soup.find_all('dl'):
        dts = dl.find_all('dt')
        dds = dl.find_all('dd')
        for dt, dd in zip(dts, dds):
            key = dt.get_text(strip=True)
            value = dd.get_text(strip=True)
            if key and value:
                lines.append(f"{key}: {value}")
    
    # Deduplicate while preserving order
    seen = set()
    unique_lines = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)
    
    return "\n".join(unique_lines)

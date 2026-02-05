"""
PaXth Template Generator - Main Streamlit Application

A maximalist web app for generating CMS templates across multiple product categories.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Optional
import os

# Import services
from services.firecrawl_service import FirecrawlService
from services.deepseek_service import DeepSeekService
from services.scraping_manager import ScrapingManager

# Import config
from config.categories import get_category_headers, get_extraction_headers, CATEGORIES, get_category_names
from config.settings import APP_TITLE, APP_ICON, APP_LAYOUT, FIRECRAWL_API_KEY, DEEPSEEK_API_KEY

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=APP_LAYOUT,
    initial_sidebar_state="expanded"
)

# Modern Minimalist CSS with Gradient Theme
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=JetBrains+Mono&display=swap');
    
    /* Root variables for dark modern theme */
    :root {
        --gradient-primary: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 50%, #10b981 100%);
        --gradient-secondary: linear-gradient(135deg, #8b5cf6 0%, #d946ef 100%);
        --gradient-accent: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
        --gradient-dark: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        --bg-dark: #0f172a;
        --bg-card: #1e293b;
        --bg-elevated: #334155;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --border-color: #334155;
        --shadow-glow: 0 8px 32px rgba(14, 165, 233, 0.2);
        --shadow-soft: 0 4px 20px rgba(0, 0, 0, 0.3);
        --border-radius: 20px;
        --border-radius-sm: 12px;
    }
    
    /* Global dark theme */
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        padding: 2rem 3rem;
        font-family: 'Poppins', sans-serif;
        color: var(--text-primary);
    }
    
    /* Remove default backgrounds */
    .stApp {
        background: var(--bg-dark);
    }
    
    /* Hide Streamlit branding - but keep sidebar controls */
    #MainMenu, footer {visibility: hidden;}
    
    /* Ensure sidebar collapse button is visible and clickable */
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        color: #0ea5e9 !important;
        background: rgba(30, 41, 59, 0.9) !important;
        border-radius: 8px !important;
        z-index: 999999 !important;
    }
    
    [data-testid="collapsedControl"]:hover {
        background: rgba(14, 165, 233, 0.2) !important;
    }
    
    button[kind="header"] {
        visibility: visible !important;
        display: flex !important;
    }
    
    /* Sidebar - Glassmorphism style */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(100, 200, 255, 0.1);
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.5);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--text-primary);
    }
    
    [data-testid="stSidebar"] hr {
        border-color: rgba(100, 200, 255, 0.15);
        margin: 1.5rem 0;
    }
    
    /* Sidebar input fields */
    [data-testid="stSidebar"] .stTextInput > div > div > input,
    [data-testid="stSidebar"] .stTextArea > div > div > textarea,
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(30, 41, 59, 0.8) !important;
        color: var(--text-primary) !important;
        border: 1.5px solid rgba(14, 165, 233, 0.3) !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div > div > div {
        color: var(--text-primary) !important;
    }
    
    [data-testid="stSidebar"] label {
        color: var(--text-secondary) !important;
        font-weight: 500;
    }
    
    /* Animated gradient header */
    .gradient-header {
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        font-size: 3rem;
        letter-spacing: -1px;
        margin-bottom: 0.5rem;
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { filter: hue-rotate(0deg); }
        50% { filter: hue-rotate(15deg); }
        100% { filter: hue-rotate(0deg); }
    }
    
    /* Glassmorphism cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(10px);
        border-radius: var(--border-radius);
        padding: 2rem;
        border: 1px solid rgba(100, 200, 255, 0.1);
        box-shadow: var(--shadow-soft);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(14, 165, 233, 0.4);
        box-shadow: var(--shadow-glow);
        transform: translateY(-2px);
    }
    
    /* Input fields - Modern dark style */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 2px solid rgba(14, 165, 233, 0.3) !important;
        border-radius: var(--border-radius-sm) !important;
        padding: 0.85rem 1.2rem !important;
        font-family: 'Poppins', sans-serif !important;
        color: var(--text-primary) !important;
        transition: all 0.3s ease !important;
        box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: var(--text-secondary) !important;
        opacity: 0.6 !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #0ea5e9 !important;
        box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.2), inset 0 2px 8px rgba(0, 0, 0, 0.2) !important;
        background: rgba(30, 41, 59, 0.95) !important;
        transform: translateY(-1px);
    }
    
    /* Selectbox dropdown */
    .stSelectbox > div > div > div {
        color: var(--text-primary) !important;
        background: rgba(30, 41, 59, 0.95) !important;
    }
    
    /* Labels */
    label {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.3px;
    }
    
    /* Primary button - Gradient with glow */
    .stButton > button[kind="primary"] {
        background: var(--gradient-primary) !important;
        border: none !important;
        border-radius: var(--border-radius-sm) !important;
        padding: 0.85rem 2.5rem !important;
        font-weight: 600 !important;
        font-family: 'Poppins', sans-serif !important;
        letter-spacing: 0.5px !important;
        color: white !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 24px rgba(14, 165, 233, 0.4) !important;
        text-transform: uppercase;
        font-size: 0.9rem !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 12px 32px rgba(14, 165, 233, 0.6) !important;
    }
    
    /* Secondary buttons - Dark glass style */
    .stButton > button {
        background: rgba(30, 41, 59, 0.6) !important;
        backdrop-filter: blur(10px);
        border: 1.5px solid rgba(14, 165, 233, 0.3) !important;
        border-radius: var(--border-radius-sm) !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 500 !important;
        font-family: 'Poppins', sans-serif !important;
        color: var(--text-primary) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: rgba(30, 41, 59, 0.9) !important;
        border-color: #0ea5e9 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(14, 165, 233, 0.3) !important;
    }
    
    /* Tabs - Modern dark style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.75rem;
        background: rgba(30, 41, 59, 0.4);
        padding: 0.75rem;
        border-radius: var(--border-radius);
        border: 1px solid rgba(14, 165, 233, 0.15);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: var(--border-radius-sm);
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-family: 'Poppins', sans-serif;
        color: var(--text-secondary);
        transition: all 0.3s ease;
        border: 1px solid transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(14, 165, 233, 0.1);
        color: #0ea5e9;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(14, 165, 233, 0.2) !important;
        color: #0ea5e9 !important;
        border: 1px solid rgba(14, 165, 233, 0.4);
        box-shadow: 0 4px 16px rgba(14, 165, 233, 0.2);
    }
    
    /* Console - Terminal style with neon glow */
    .console-box {
        background: linear-gradient(135deg, #0a0e1a 0%, #0d1117 100%);
        color: #00ff9d;
        padding: 1.5rem;
        border-radius: var(--border-radius);
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 13px;
        height: 450px;
        overflow-y: auto;
        white-space: pre-wrap;
        border: 1px solid rgba(0, 255, 157, 0.2);
        box-shadow: 0 0 30px rgba(0, 255, 157, 0.1), inset 0 0 30px rgba(0, 0, 0, 0.5);
    }
    
    .console-box::-webkit-scrollbar {
        width: 10px;
    }
    
    .console-box::-webkit-scrollbar-track {
        background: rgba(0, 255, 157, 0.05);
        border-radius: 5px;
    }
    
    .console-box::-webkit-scrollbar-thumb {
        background: rgba(0, 255, 157, 0.3);
        border-radius: 5px;
    }
    
    .console-box::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 255, 157, 0.5);
    }
    
    /* Expander - Glass style */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid rgba(14, 165, 233, 0.2) !important;
        border-radius: var(--border-radius-sm) !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
        padding: 1rem !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(30, 41, 59, 0.8) !important;
        border-color: rgba(14, 165, 233, 0.4) !important;
    }
    
    /* Metrics - Neon cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.1) 0%, rgba(6, 182, 212, 0.05) 100%);
        padding: 1.5rem;
        border-radius: var(--border-radius-sm);
        border: 1px solid rgba(14, 165, 233, 0.3);
        box-shadow: 0 4px 16px rgba(14, 165, 233, 0.1);
    }
    
    [data-testid="stMetricValue"] {
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-weight: 500;
    }
    
    /* File uploader - Glass style */
    [data-testid="stFileUploader"] {
        background: rgba(30, 41, 59, 0.4);
        border: 2px dashed rgba(14, 165, 233, 0.4);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #0ea5e9;
        background: rgba(14, 165, 233, 0.05);
        box-shadow: 0 0 20px rgba(14, 165, 233, 0.2);
    }
    
    [data-testid="stFileUploader"] label {
        color: #0ea5e9 !important;
        font-weight: 500;
    }
    
    /* Messages - Modern alerts */
    .stSuccess {
        background: rgba(16, 185, 129, 0.15) !important;
        border-left: 4px solid #10b981 !important;
        border-radius: var(--border-radius-sm) !important;
        color: #34d399 !important;
    }
    
    .stWarning {
        background: rgba(245, 158, 11, 0.15) !important;
        border-left: 4px solid #f59e0b !important;
        border-radius: var(--border-radius-sm) !important;
        color: #fbbf24 !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.15) !important;
        border-left: 4px solid #ef4444 !important;
        border-radius: var(--border-radius-sm) !important;
        color: #f87171 !important;
    }
    
    .stInfo {
        background: rgba(14, 165, 233, 0.15) !important;
        border-left: 4px solid #0ea5e9 !important;
        border-radius: var(--border-radius-sm) !important;
        color: #38bdf8 !important;
    }
    
    /* Divider - Neon glow */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(14, 165, 233, 0.5), transparent);
        margin: 2rem 0;
        box-shadow: 0 0 10px rgba(14, 165, 233, 0.3);
    }
    
    /* Dataframe - Dark glass */
    .stDataFrame {
        background: rgba(30, 41, 59, 0.6) !important;
        border-radius: var(--border-radius) !important;
        border: 1px solid rgba(14, 165, 233, 0.2);
    }
    
    /* Download button - Accent gradient */
    .stDownloadButton > button {
        background: var(--gradient-accent) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: 0 8px 24px rgba(245, 158, 11, 0.3) !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 32px rgba(245, 158, 11, 0.5) !important;
    }
    
    /* Spinner - Cyan glow */
    .stSpinner > div {
        border-color: #0ea5e9 transparent transparent transparent !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: var(--gradient-primary) !important;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "console_logs" not in st.session_state:
        st.session_state.console_logs = []
    if "extraction_results" not in st.session_state:
        st.session_state.extraction_results = None
    if "final_values" not in st.session_state:
        st.session_state.final_values = {}
    if "form_data" not in st.session_state:
        st.session_state.form_data = None
    if "processing_done" not in st.session_state:
        st.session_state.processing_done = False


def log(message: str):
    """Add log message with timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.console_logs.append(f"[{timestamp}] {message}")


def clear_logs():
    """Clear all logs."""
    st.session_state.console_logs = []


def process_extraction(form_data: dict, category: str):
    """Run the full extraction pipeline."""
    clear_logs()
    
    log("🚀 Starting CMS Template Extraction...")
    log(f"📦 Category: {category}")
    log(f"📋 SKU: {form_data.get('sku', 'N/A')}")
    
    # Get MM43 context data
    mm43_data = form_data.get("mm43", "")
    if mm43_data:
        log(f"📊 MM43 Data provided: {len(mm43_data)} characters")
    
    urls = [
        form_data.get("url1", ""),
        form_data.get("url2", ""),
        form_data.get("url3", "")
    ]
    methods = [
        form_data.get("method1", "Auto"),
        form_data.get("method2", "Auto"),
        form_data.get("method3", "Auto")
    ]
    valid_urls = [u for u in urls if u and u.strip()]
    log(f"🔗 URLs to process: {len(valid_urls)}")
    
    # Check for PDF
    pdf_file = form_data.get("pdf_file")
    pdf_content = ""
    if pdf_file:
        log("📄 PDF file uploaded - extracting text...")
        try:
            import PyPDF2
            import io
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
            pdf_text_parts = []
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if text:
                    pdf_text_parts.append(f"[Page {page_num + 1}]\n{text}")
            pdf_content = "\n\n".join(pdf_text_parts)
            log(f"✅ PDF: Extracted {len(pdf_content)} characters from {len(pdf_reader.pages)} pages")
        except ImportError:
            log("⚠️ PDF extraction requires PyPDF2. Install with: pip install PyPDF2")
        except Exception as e:
            log(f"❌ PDF extraction error: {str(e)}")
    
    # Check API keys
    if not DEEPSEEK_API_KEY:
        log("❌ ERROR: DeepSeek API key not configured!")
        log("   Please add DEEPSEEK_API_KEY to .env file")
        return {}
    
    log(f"✅ DeepSeek API Key configured")
    
    # Step 1: Scrape URLs
    log("\n" + "="*50)
    log("STEP 1: SCRAPING URLs")
    log("="*50)
    
    manager = ScrapingManager()
    scraped_results = {}
    saved_files = []
    
    for i, url in enumerate(urls):
        url_key = f"url{i+1}"
        method = methods[i]
        if url and url.strip():
            log(f"\nProcessing URL {i+1} ({method}): {url[:50]}...")
            result = manager.scrape_url(url.strip(), method=method, log_callback=log)
            scraped_results[url_key] = result
            
            if result.get("success"):
                if result.get("filename"):
                    saved_files.append(result.get("filename"))
                log(f"✅ URL {i+1}: Got {len(result.get('markdown', ''))} characters")
            else:
                log(f"❌ URL {i+1}: Failed - {result.get('error', 'Unknown error')}")
        else:
            scraped_results[url_key] = {"success": False, "markdown": "", "error": "Empty URL"}
            log(f"⏭️ URL {i+1}: Skipped (empty)")
    
    # Add PDF content as a source if available
    if pdf_content:
        scraped_results["pdf"] = {"success": True, "markdown": pdf_content, "error": None}
        log(f"📄 Added PDF content as source")
    
    # Display saved files info
    if saved_files:
        log("\n📁 SAVED MARKDOWN FILES:")
        for filename in saved_files:
            log(f"   ✓ {filename}")
    
    # Step 2: Extract with DeepSeek
    log("\n" + "="*50)
    log("STEP 2: EXTRACTING ATTRIBUTES WITH DEEPSEEK")
    log("="*50)
    
    extraction_headers = get_extraction_headers(category)
    log(f"📊 Extracting {len(extraction_headers)} attributes...")
    
    deepseek = DeepSeekService()
    extraction_results = deepseek.extract_from_multiple_sources(
        scraped_results,
        extraction_headers,
        category,
        log,
        mm43_context=mm43_data  # Pass MM43 data for better accuracy
    )
    
    log("\n" + "="*50)
    log("✅ EXTRACTION COMPLETE!")
    log("="*50)
    
    # Count extracted values
    total_extracted = 0
    for header, values in extraction_results.items():
        for url_key, val in values.items():
            if val:
                total_extracted += 1
    
    log(f"📈 Total values extracted: {total_extracted}")
    
    return extraction_results


def render_sidebar():
    """Render sidebar with settings."""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">⚡</div>
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; font-size: 1.4rem; letter-spacing: -0.5px;">PaXth Template Generator</div>
            <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem; margin-top: 0.25rem;">v2.0</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Category selection
        st.markdown('<p style="color: rgba(255,255,255,0.7); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;">📦 Category</p>', unsafe_allow_html=True)
        category = st.selectbox(
            "Select Category",
            options=get_category_names(),
            key="category_select",
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Mode selection
        st.markdown('<p style="color: rgba(255,255,255,0.7); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;">⚙️ Mode</p>', unsafe_allow_html=True)
        mode = st.radio(
            "Processing Mode",
            ["Single SKU", "Batch Processing"],
            key="mode_select",
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # API Status with modern badges
        st.markdown('<p style="color: rgba(255,255,255,0.7); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.75rem;">🔑 API Status</p>', unsafe_allow_html=True)
        
        fc_status = FIRECRAWL_API_KEY
        ds_status = DEEPSEEK_API_KEY
        
        fc_badge = '<span style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; background: rgba(16, 185, 129, 0.15); color: #34d399;">● Active</span>' if fc_status else '<span style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; background: rgba(239, 68, 68, 0.15); color: #f87171;">○ Missing</span>'
        ds_badge = '<span style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; background: rgba(16, 185, 129, 0.15); color: #34d399;">● Active</span>' if ds_status else '<span style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; background: rgba(239, 68, 68, 0.15); color: #f87171;">○ Missing</span>'
        
        st.markdown(f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;"><span style="color: rgba(255,255,255,0.8); font-size: 0.85rem;">Firecrawl</span>{fc_badge}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="display: flex; justify-content: space-between; align-items: center;"><span style="color: rgba(255,255,255,0.8); font-size: 0.85rem;">DeepSeek</span>{ds_badge}</div>', unsafe_allow_html=True)
        
        if not FIRECRAWL_API_KEY or not DEEPSEEK_API_KEY:
            st.markdown("<br>", unsafe_allow_html=True)
            st.warning("⚠️ Add missing API keys to .env")
        
        st.markdown("---")
        
        # Reset button
        if st.button("🔄 Reset Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        # Footer
        st.markdown("""
        <div style="position: absolute; bottom: 1rem; left: 0; right: 0; text-align: center; color: rgba(255,255,255,0.3); font-size: 0.7rem;">
        </div>
        """, unsafe_allow_html=True)
    
    return category, mode


def render_input_form(category: str):
    """Render the input form."""
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 600; font-size: 1.5rem; margin: 0;">Product Information</h2>
        <p style="color: #6b7280; font-size: 0.9rem; margin-top: 0.25rem;">Enter the product details below to begin extraction</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Row 1: Basic product info in a clean grid
    st.markdown('<p style="color: #374151; font-weight: 600; font-size: 0.9rem; margin-bottom: 0.75rem;">📋 Basic Details</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sku = st.text_input("SKU *", key="input_sku", placeholder="e.g., PROD-001")
        base_code = st.text_input("Base Code *", key="input_base_code", placeholder="e.g., BC001")
        ean = st.text_input("EAN", key="input_ean", placeholder="e.g., 1234567890123")
    
    with col2:
        shipping_weight = st.text_input("Shipping Weight", key="input_weight", placeholder="e.g., 2.5 kg")
        color = st.text_input("Color", key="input_color", placeholder="e.g., Black")
        product_type = st.text_input("Product Type", key="input_type", placeholder=category)
    
    with col3:
        st.markdown('<p style="font-size: 0.875rem; color: #374151; font-weight: 500; margin-bottom: 0.5rem;">MM43 Data</p>', unsafe_allow_html=True)
        mm43 = st.text_area(
            "MM43 Info",
            key="input_mm43",
            placeholder="Paste MM43 product data here for improved extraction accuracy...",
            height=127,
            label_visibility="collapsed"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Row 2: PDF Upload with better styling
    st.markdown('<p style="color: #374151; font-weight: 600; font-size: 0.9rem; margin-bottom: 0.75rem;">📄 Product Specification PDF <span style="color: #9ca3af; font-weight: 400;">(Optional)</span></p>', unsafe_allow_html=True)
    pdf_file = st.file_uploader(
        "Upload product spec sheet or datasheet PDF",
        type=["pdf"],
        key="input_pdf",
        help="PDF content will be extracted and used for attribute mapping",
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Row 3: URLs with cleaner layout
    st.markdown('<p style="color: #374151; font-weight: 600; font-size: 0.9rem; margin-bottom: 0.25rem;">🔗 Product URLs</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: #9ca3af; font-size: 0.8rem; margin-bottom: 1rem;">Enter at least one URL or upload a PDF above</p>', unsafe_allow_html=True)
    
    # URL 1 with method
    col_url1, col_method1 = st.columns([4, 1])
    with col_url1:
        url1 = st.text_input("URL 1", key="input_url1", placeholder="https://www.example.com/product-page", label_visibility="collapsed")
    with col_method1:
        method1 = st.selectbox("Method", ["Auto", "BS4", "Crawl4AI", "Playwright", "Firecrawl"], key="method_url1", index=0, label_visibility="collapsed")
    
    # URL 2 with method
    col_url2, col_method2 = st.columns([4, 1])
    with col_url2:
        url2 = st.text_input("URL 2", key="input_url2", placeholder="https://www.example.com/product-page", label_visibility="collapsed")
    with col_method2:
        method2 = st.selectbox("Method", ["Auto", "BS4", "Crawl4AI", "Playwright", "Firecrawl"], key="method_url2", index=0, label_visibility="collapsed")
    
    # URL 3 with method
    col_url3, col_method3 = st.columns([4, 1])
    with col_url3:
        url3 = st.text_input("URL 3", key="input_url3", placeholder="https://www.example.com/product-page", label_visibility="collapsed")
    with col_method3:
        method3 = st.selectbox("Method", ["Auto", "BS4", "Crawl4AI", "Playwright", "Firecrawl"], key="method_url3", index=0, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Validation: SKU and base_code required, PLUS either URL or PDF
    has_url = bool(url1 or url2 or url3)
    has_pdf = pdf_file is not None
    is_valid = bool(sku and base_code and (has_url or has_pdf))
    
    # Centered extract button with gradient
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    with col2:
        extract_clicked = st.button(
            "⚡ Extract & Map Attributes",
            type="primary",
            use_container_width=True,
            disabled=not is_valid
        )
    
    if not is_valid:
        st.markdown("<br>", unsafe_allow_html=True)
        if not sku or not base_code:
            st.info("💡 Fill in SKU and Base Code to enable extraction")
        elif not has_url and not has_pdf:
            st.info("💡 Provide at least one URL or upload a PDF")
    
    if extract_clicked and is_valid:
        form_data = {
            "sku": sku,
            "base_code": base_code,
            "ean": ean,
            "shipping_weight": shipping_weight,
            "color": color,
            "product_type": product_type or category,
            "mm43": mm43,
            "pdf_file": pdf_file,
            "url1": url1,
            "url2": url2,
            "url3": url3,
            "method1": method1,
            "method2": method2,
            "method3": method3
        }
        return form_data
    
    return None


def render_results_table(results: dict, headers: list):
    """Render the interactive results table."""
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 600; font-size: 1.5rem; margin: 0;">Extraction Results</h2>
        <p style="color: #6b7280; font-size: 0.9rem; margin-top: 0.25rem;">Click any value to select it for the Final Output column</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not results:
        st.warning("No extraction results available. Run extraction first.")
        return
    
    # Store results in session state for button access
    st.session_state.current_results = results
    st.session_state.current_headers = headers
    
    # Initialize final values
    if "final_values" not in st.session_state:
        st.session_state.final_values = {}
    
    # Action buttons with modern styling
    st.markdown('<p style="color: #374151; font-weight: 600; font-size: 0.85rem; margin-bottom: 0.75rem;">⚡ Quick Actions</p>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("🎯 Auto-fill Best", key="autofill_best", use_container_width=True):
            for idx, header in enumerate(headers):
                url_values = results.get(header, {})
                for key in ["url1", "url2", "url3", "pdf"]:
                    val = url_values.get(key, "")
                    if val and str(val).strip():
                        st.session_state.final_values[header] = str(val)
                        st.session_state[f"text_final_{idx}"] = str(val)
                        break
            st.rerun()
    
    with col2:
        if st.button("1️⃣ Use URL 1", key="use_url1", use_container_width=True):
            for idx, header in enumerate(headers):
                val = results.get(header, {}).get("url1", "")
                if val and str(val).strip():
                    st.session_state.final_values[header] = str(val)
                    st.session_state[f"text_final_{idx}"] = str(val)
            st.rerun()
    
    with col3:
        if st.button("2️⃣ Use URL 2", key="use_url2", use_container_width=True):
            for idx, header in enumerate(headers):
                val = results.get(header, {}).get("url2", "")
                if val and str(val).strip():
                    st.session_state.final_values[header] = str(val)
                    st.session_state[f"text_final_{idx}"] = str(val)
            st.rerun()
    
    with col4:
        if st.button("3️⃣ Use URL 3", key="use_url3", use_container_width=True):
            for idx, header in enumerate(headers):
                val = results.get(header, {}).get("url3", "")
                if val and str(val).strip():
                    st.session_state.final_values[header] = str(val)
                    st.session_state[f"text_final_{idx}"] = str(val)
            st.rerun()
    
    with col5:
        if st.button("🗑️ Clear All", key="clear_all", use_container_width=True):
            st.session_state.final_values = {}
            for idx in range(len(headers)):
                if f"text_final_{idx}" in st.session_state:
                    st.session_state[f"text_final_{idx}"] = ""
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Table header with gradient background
    st.markdown("""
    <div style="display: grid; grid-template-columns: 2fr 1.5fr 1.5fr 1.5fr 2fr; gap: 0.5rem; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); padding: 0.75rem 1rem; border-radius: 10px; margin-bottom: 0.5rem; font-weight: 600; color: #374151; font-size: 0.85rem;">
        <div>Attribute</div>
        <div>URL 1</div>
        <div>URL 2</div>
        <div>URL 3</div>
        <div>Final Output</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Render rows
    for idx, header in enumerate(headers):
        url_values = results.get(header, {})
        url1_val = str(url_values.get("url1", "") or "")
        url2_val = str(url_values.get("url2", "") or "")
        url3_val = str(url_values.get("url3", "") or "")
        
        cols = st.columns([2, 1.5, 1.5, 1.5, 2])
        
        # Attribute name with subtle styling
        display_header = f"{header[:28]}..." if len(header) > 28 else header
        cols[0].markdown(f'<p style="font-weight: 500; color: #374151; font-size: 0.9rem; margin: 0.5rem 0;">{display_header}</p>', unsafe_allow_html=True)
        
        # URL 1 value button
        if url1_val:
            btn_label = f"{url1_val[:18]}..." if len(url1_val) > 18 else url1_val
            if cols[1].button(f"📋 {btn_label}", key=f"u1_{idx}_{header}", use_container_width=True):
                st.session_state.final_values[header] = url1_val
                st.session_state[f"text_final_{idx}"] = url1_val
                st.rerun()
        else:
            cols[1].markdown('<p style="color: #d1d5db; font-size: 0.85rem; text-align: center;">—</p>', unsafe_allow_html=True)
        
        # URL 2 value button
        if url2_val:
            btn_label = f"{url2_val[:18]}..." if len(url2_val) > 18 else url2_val
            if cols[2].button(f"📋 {btn_label}", key=f"u2_{idx}_{header}", use_container_width=True):
                st.session_state.final_values[header] = url2_val
                st.session_state[f"text_final_{idx}"] = url2_val
                st.rerun()
        else:
            cols[2].markdown('<p style="color: #d1d5db; font-size: 0.85rem; text-align: center;">—</p>', unsafe_allow_html=True)
        
        # URL 3 value button
        if url3_val:
            btn_label = f"{url3_val[:18]}..." if len(url3_val) > 18 else url3_val
            if cols[3].button(f"📋 {btn_label}", key=f"u3_{idx}_{header}", use_container_width=True):
                st.session_state.final_values[header] = url3_val
                st.session_state[f"text_final_{idx}"] = url3_val
                st.rerun()
        else:
            cols[3].markdown('<p style="color: #d1d5db; font-size: 0.85rem; text-align: center;">—</p>', unsafe_allow_html=True)
        
        # Final output - editable text input synced with session state
        current_final = st.session_state.final_values.get(header, "")
        if f"text_final_{idx}" not in st.session_state:
            st.session_state[f"text_final_{idx}"] = current_final
        
        new_val = cols[4].text_input(
            "final", 
            value=current_final,
            key=f"text_final_{idx}",
            label_visibility="collapsed",
            on_change=lambda h=header, i=idx: st.session_state.final_values.update({h: st.session_state[f"text_final_{i}"]})
        )


def render_export(form_data: dict, headers: list, category: str):
    """Render export section."""
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h3 style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 600; font-size: 1.25rem; margin: 0;">Export Data</h3>
    </div>
    """, unsafe_allow_html=True)
    
    final_values = st.session_state.get("final_values", {})
    filled = sum(1 for v in final_values.values() if v)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Progress indicator
        progress_pct = filled / len(headers) if headers else 0
        st.markdown(f"""
        <div style="background: #f3f4f6; border-radius: 10px; padding: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-weight: 500; color: #374151;">Attributes Filled</span>
                <span style="font-weight: 700; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{filled} / {len(headers)}</span>
            </div>
            <div style="background: #e5e7eb; border-radius: 999px; height: 8px; overflow: hidden;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100%; width: {progress_pct * 100}%; border-radius: 999px; transition: width 0.3s ease;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Build export data
        export_row = {}
        
        if form_data:
            export_row["sku"] = form_data.get("sku", "")
            export_row["base_code"] = form_data.get("base_code", "")
            export_row["attributes__lulu_ean"] = form_data.get("ean", "")
            export_row["attributes__shipping_weight"] = form_data.get("shipping_weight", "")
            export_row["attributes__color"] = form_data.get("color", "")
        
        for header in headers:
            if header not in export_row:
                export_row[header] = final_values.get(header, "")
        
        df = pd.DataFrame([export_row])
        csv = df.to_csv(index=False)
        
        sku = form_data.get("sku", "export") if form_data else "export"
        
        st.download_button(
            "📥 Download CSV",
            csv,
            f"{category}_{sku}.csv",
            "text/csv",
            type="primary",
            use_container_width=True
        )


def render_console():
    """Render console output."""
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h3 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 600; font-size: 1.25rem; margin: 0;">Console Output</h3>
        <p style="color: #6b7280; font-size: 0.85rem; margin-top: 0.25rem;">Real-time processing logs and status updates</p>
    </div>
    """, unsafe_allow_html=True)
    
    logs = st.session_state.get("console_logs", [])
    
    if logs:
        log_html = []
        for log_line in logs:
            if "✅" in log_line or "COMPLETE" in log_line:
                color = "#34d399"  # Emerald
            elif "❌" in log_line or "ERROR" in log_line:
                color = "#f87171"  # Red
            elif "⚠️" in log_line or "WARNING" in log_line:
                color = "#fbbf24"  # Amber
            elif "🔥" in log_line or "🤖" in log_line or "📊" in log_line:
                color = "#60a5fa"  # Blue
            elif "=" in log_line:
                color = "#6b7280"  # Gray
            else:
                color = "#e5e7eb"  # Light gray
            log_html.append(f'<span style="color: {color};">{log_line}</span><br>')
        
        st.markdown(
            f'<div class="console-box">{"".join(log_html)}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="console-box" style="color: #6b7280; display: flex; align-items: center; justify-content: center; height: 400px;"><div style="text-align: center;"><div style="font-size: 2rem; margin-bottom: 0.5rem;">⌛</div><div>Waiting for operations...</div></div></div>',
            unsafe_allow_html=True
        )
    
    if logs:
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            if st.button("🗑️ Clear Logs", use_container_width=True):
                clear_logs()
                st.rerun()


def render_saved_markdown_files():
    """Render a section to browse saved markdown files."""
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h3 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 600; font-size: 1.25rem; margin: 0;">Saved Files</h3>
        <p style="color: #6b7280; font-size: 0.85rem; margin-top: 0.25rem;">Browse and download extracted markdown files</p>
    </div>
    """, unsafe_allow_html=True)
    
    from pathlib import Path
    mdfiles_dir = Path("mdfiles")
    
    if not mdfiles_dir.exists():
        st.markdown("""
        <div style="background: linear-gradient(145deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 12px; padding: 2rem; text-align: center; border: 1px dashed #e5e7eb;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📂</div>
            <div style="color: #6b7280; font-size: 0.9rem;">No files yet. Run extraction to save markdown files.</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    md_files = sorted(list(mdfiles_dir.glob("*.md")), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not md_files:
        st.markdown("""
        <div style="background: linear-gradient(145deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 12px; padding: 2rem; text-align: center; border: 1px dashed #e5e7eb;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📂</div>
            <div style="color: #6b7280; font-size: 0.9rem;">No markdown files found.</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 1.25rem;">📊</span>
        <span style="font-weight: 500; color: #374151;">{len(md_files)} files saved</span>
    </div>
    """, unsafe_allow_html=True)
    
    if len(md_files) > 0:
        file_options = [f.name for f in md_files]
        selected_file = st.selectbox("Select a file to view:", file_options, key="md_file_select", label_visibility="collapsed")
        
        if selected_file:
            filepath = mdfiles_dir / selected_file
            
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                file_size = filepath.stat().st_size
                st.markdown(f"""
                <div style="background: #f9fafb; border-radius: 8px; padding: 0.75rem 1rem; margin: 1rem 0; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-family: monospace; color: #374151; font-size: 0.9rem;">📄 {selected_file}</span>
                    <span style="color: #6b7280; font-size: 0.8rem;">{file_size:,} bytes</span>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("📖 View Content", expanded=False):
                    st.markdown(content)
                
                col1, col2, col3 = st.columns([1, 1, 3])
                with col1:
                    st.download_button(
                        "📥 Download",
                        content,
                        selected_file,
                        "text/markdown",
                        use_container_width=True
                    )
                
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")


def main():
    """Main application."""
    init_session_state()
    
    # Sidebar
    category, mode = render_sidebar()
    
    # Modern Header
    st.markdown(f"""
    <div style="margin-bottom: 1.5rem;">
        <h1 class="gradient-header">{APP_TITLE}</h1>
        <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
            <span style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; color: #667eea; font-weight: 500;">📦 {category}</span>
            <span style="background: rgba(16, 185, 129, 0.1); padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; color: #059669; font-weight: 500;">⚙️ {mode}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get headers
    all_headers = get_category_headers(category)
    extraction_headers = get_extraction_headers(category)
    
    # Collapsible headers info with modern styling
    with st.expander(f"📋 View {category} Attributes ({len(all_headers)} total)", expanded=False):
        st.markdown("""
        <div style="background: linear-gradient(145deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 10px; padding: 1rem;">
        """, unsafe_allow_html=True)
        cols = st.columns(3)
        for i, h in enumerate(all_headers):
            cols[i % 3].markdown(f"<span style='color: #374151; font-size: 0.85rem;'>• {h}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Modern Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Input", "📊 Results", "🖥️ Console", "📁 Files"])
    
    with tab1:
        if mode == "Single SKU":
            form_data = render_input_form(category)
            
            if form_data:
                st.session_state.form_data = form_data
                
                with st.spinner("⚡ Processing... Check Console tab for live updates"):
                    results = process_extraction(form_data, category)
                    st.session_state.extraction_results = results
                    st.session_state.processing_done = True
                
                st.success("✅ Extraction complete! Switch to the Results tab to review.")
                st.rerun()
        else:
            st.markdown("""
            <div style="background: linear-gradient(145deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 12px; padding: 1.5rem; text-align: center; border: 1px dashed #e5e7eb; margin-top: 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📁</div>
                <div style="color: #374151; font-weight: 500; margin-bottom: 0.5rem;">Batch Processing</div>
                <div style="color: #6b7280; font-size: 0.9rem;">Upload a CSV file with columns: sku, base_code, ean, url1, url2, url3</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            uploaded = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")
            if uploaded:
                df = pd.read_csv(uploaded)
                st.dataframe(df, use_container_width=True)
                st.info("🚧 Batch processing coming soon!")
    
    with tab2:
        if st.session_state.get("extraction_results"):
            render_results_table(st.session_state.extraction_results, extraction_headers)
            render_export(st.session_state.form_data, all_headers, category)
        else:
            st.markdown("""
            <div style="background: linear-gradient(145deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 12px; padding: 3rem; text-align: center; border: 1px dashed #e5e7eb; margin-top: 1rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
                <div style="color: #374151; font-weight: 500; font-size: 1.1rem; margin-bottom: 0.5rem;">No Results Yet</div>
                <div style="color: #6b7280; font-size: 0.9rem;">Fill the input form and click 'Extract & Map' to see results</div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        render_console()
    
    with tab4:
        render_saved_markdown_files()


if __name__ == "__main__":
    main()

"""
Sidebar component for category selection and mode toggle.
"""
import streamlit as st
from config.categories import get_category_names


def render_sidebar():
    """
    Render the sidebar with category selection and processing mode.
    
    Returns:
        tuple: (selected_category, processing_mode)
    """
    with st.sidebar:
        st.markdown("## 🏭 CMS Template Generator")
        st.markdown("---")
        
        # Category Selection
        st.markdown("### 📦 Select Category")
        categories = get_category_names()
        selected_category = st.selectbox(
            "Product Category",
            options=categories,
            index=0,
            help="Select the product category to load relevant attribute headers"
        )
        
        st.markdown("---")
        
        # Processing Mode
        st.markdown("### ⚙️ Processing Mode")
        processing_mode = st.radio(
            "Select Mode",
            options=["Single SKU", "Batch Processing"],
            index=0,
            help="Single SKU: Enter one product manually\nBatch: Upload CSV with multiple products"
        )
        
        st.markdown("---")
        
        # API Status
        st.markdown("### 🔑 API Status")
        
        from config.settings import FIRECRAWL_API_KEY, DEEPSEEK_API_KEY
        
        firecrawl_status = "✅ Configured" if FIRECRAWL_API_KEY else "❌ Not Set"
        deepseek_status = "✅ Configured" if DEEPSEEK_API_KEY else "❌ Not Set"
        
        st.markdown(f"**Firecrawl:** {firecrawl_status}")
        st.markdown(f"**DeepSeek:** {deepseek_status}")
        
        if not FIRECRAWL_API_KEY or not DEEPSEEK_API_KEY:
            st.warning("⚠️ Configure API keys in `.env` file")
            
        st.markdown("---")
        
        # Instructions
        with st.expander("📖 How to Use", expanded=False):
            st.markdown("""
            1. **Select Category** - Choose product type
            2. **Choose Mode** - Single or Batch
            3. **Enter Details** - Fill in product info
            4. **Add URLs** - Product page URLs to scrape
            5. **Map & Extract** - Process and extract data
            6. **Review & Edit** - Click values to select
            7. **Export** - Download as CSV
            """)
            
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: #666; font-size: 12px;'>"
            "CMS Template Generator v1.0"
            "</div>",
            unsafe_allow_html=True
        )
        
    return selected_category, processing_mode

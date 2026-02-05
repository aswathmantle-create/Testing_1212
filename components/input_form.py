"""
Input form component for SKU data entry.
"""
import streamlit as st
import pandas as pd
from typing import Optional
from config.categories import DEFAULT_INPUT_FIELDS


def render_input_form(processing_mode: str, category: str) -> Optional[dict]:
    """
    Render the input form based on processing mode.
    
    Args:
        processing_mode: "Single SKU" or "Batch Processing"
        category: Selected product category
        
    Returns:
        dict with input data or None if not submitted
    """
    st.markdown("## 📝 Product Information")
    
    if processing_mode == "Single SKU":
        return _render_single_sku_form(category)
    else:
        return _render_batch_form(category)


def _render_single_sku_form(category: str) -> Optional[dict]:
    """Render form for single SKU input."""
    
    with st.container():
        st.markdown("### Enter Product Details")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sku = st.text_input("SKU *", placeholder="e.g., PROD-001", key="sku")
            base_code = st.text_input("Base Code *", placeholder="e.g., BC001", key="base_code")
            ean = st.text_input("EAN", placeholder="e.g., 1234567890123", key="ean")
            
        with col2:
            shipping_weight = st.text_input("Shipping Weight", placeholder="e.g., 2.5 kg", key="shipping_weight")
            color = st.text_input("Color", placeholder="e.g., Black", key="color")
            product_type = st.text_input("Product Type", placeholder=f"e.g., {category}", key="product_type")
            
        with col3:
            st.markdown("**Product URLs (for scraping)**")
            url1 = st.text_input("URL 1 *", placeholder="https://...", key="url1")
            url2 = st.text_input("URL 2", placeholder="https://...", key="url2")
            url3 = st.text_input("URL 3", placeholder="https://...", key="url3")
    
    st.markdown("---")
    
    # Store form data in session state
    form_data = {
        "sku": sku,
        "base_code": base_code,
        "ean": ean,
        "shipping_weight": shipping_weight,
        "color": color,
        "product_type": product_type or category,
        "url1": url1,
        "url2": url2,
        "url3": url3,
        "mode": "single"
    }
    
    # Validation
    is_valid = sku and base_code and url1
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Map & Extract", type="primary", use_container_width=True, disabled=not is_valid):
            if is_valid:
                st.session_state.form_submitted = True
                st.session_state.form_data = form_data
                return form_data
            else:
                st.error("Please fill in required fields (SKU, Base Code, URL 1)")
                
    if not is_valid:
        st.info("ℹ️ Fill in required fields (*) to enable extraction")
        
    return None


def _render_batch_form(category: str) -> Optional[dict]:
    """Render form for batch CSV upload."""
    
    with st.container():
        st.markdown("### Upload Batch CSV")
        
        # Show expected format
        with st.expander("📋 Expected CSV Format", expanded=False):
            st.markdown("Your CSV should have these headers:")
            st.code("sku,base_code,ean,shipping_weight,color,product_type,url1,url2,url3")
            
            # Sample data
            sample_df = pd.DataFrame({
                "sku": ["SKU001", "SKU002"],
                "base_code": ["BC001", "BC002"],
                "ean": ["1234567890123", "1234567890124"],
                "shipping_weight": ["2.5 kg", "3.0 kg"],
                "color": ["Black", "White"],
                "product_type": [category, category],
                "url1": ["https://example.com/prod1", "https://example.com/prod2"],
                "url2": ["https://amazon.com/prod1", "https://amazon.com/prod2"],
                "url3": ["", "https://ebay.com/prod2"]
            })
            st.dataframe(sample_df, use_container_width=True)
            
            # Download sample template
            csv = sample_df.to_csv(index=False)
            st.download_button(
                "📥 Download Sample Template",
                csv,
                "sample_template.csv",
                "text/csv",
                key="download_sample"
            )
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload CSV File",
            type=["csv"],
            help="Upload a CSV file with the required headers"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ Loaded {len(df)} rows from CSV")
                
                # Validate headers
                required_headers = {"sku", "base_code", "url1"}
                missing_headers = required_headers - set(df.columns)
                
                if missing_headers:
                    st.error(f"❌ Missing required headers: {', '.join(missing_headers)}")
                    return None
                
                # Preview data
                st.markdown("#### Preview")
                st.dataframe(df.head(10), use_container_width=True)
                
                if len(df) > 10:
                    st.info(f"Showing first 10 of {len(df)} rows")
                
                st.markdown("---")
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("🚀 Map & Extract All", type="primary", use_container_width=True):
                        form_data = {
                            "dataframe": df,
                            "mode": "batch",
                            "row_count": len(df)
                        }
                        st.session_state.form_submitted = True
                        st.session_state.form_data = form_data
                        return form_data
                        
            except Exception as e:
                st.error(f"❌ Error reading CSV: {str(e)}")
                return None
                
    return None


def get_urls_from_form_data(form_data: dict) -> list:
    """Extract URLs from form data."""
    if form_data.get("mode") == "single":
        urls = []
        for key in ["url1", "url2", "url3"]:
            url = form_data.get(key, "")
            urls.append(url if url else "")
        return urls
    return []

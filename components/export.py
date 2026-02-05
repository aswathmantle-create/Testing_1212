"""
Export functionality for CSV generation.
"""
import streamlit as st
import pandas as pd
from typing import Dict, List
from io import StringIO


def export_to_csv(
    final_values: Dict[str, str],
    input_data: dict,
    headers: List[str],
    category: str
) -> str:
    """
    Generate CSV content from final values and input data.
    
    Args:
        final_values: Dict mapping header to final value
        input_data: Original input data from form
        headers: List of all attribute headers for the category
        category: Product category name
        
    Returns:
        CSV string content
    """
    # Build row data
    row_data = {}
    
    # Add input fields first
    if input_data.get("mode") == "single":
        row_data["sku"] = input_data.get("sku", "")
        row_data["base_code"] = input_data.get("base_code", "")
        row_data["attributes__lulu_ean"] = input_data.get("ean", "")
        row_data["attributes__shipping_weight"] = input_data.get("shipping_weight", "")
        row_data["attributes__color"] = input_data.get("color", "")
        row_data["attributes__product_type"] = input_data.get("product_type", "")
    
    # Add all headers with their final values
    for header in headers:
        if header not in row_data:  # Don't overwrite input fields
            row_data[header] = final_values.get(header, "")
    
    # Create DataFrame
    df = pd.DataFrame([row_data])
    
    # Reorder columns to match header order
    ordered_columns = [h for h in headers if h in df.columns]
    df = df[ordered_columns]
    
    return df.to_csv(index=False)


def render_export_button(
    final_values: Dict[str, str],
    input_data: dict,
    headers: List[str],
    category: str
):
    """
    Render the export button with download functionality.
    
    Args:
        final_values: Dict mapping header to final value
        input_data: Original input data from form
        headers: List of all attribute headers
        category: Product category name
    """
    st.markdown("---")
    st.markdown("## 📥 Export Results")
    
    # Count filled values
    filled_count = sum(1 for v in final_values.values() if v)
    total_count = len(headers)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.metric("Attributes Filled", f"{filled_count} / {total_count}")
        
        if filled_count < total_count * 0.5:
            st.warning("⚠️ Less than 50% of attributes are filled. Consider reviewing the data.")
    
    with col2:
        # Generate CSV
        csv_content = export_to_csv(final_values, input_data, headers, category)
        
        # Get SKU for filename
        sku = input_data.get("sku", "export")
        filename = f"{category}_{sku}_template.csv"
        
        st.download_button(
            label="📥 Export as CSV",
            data=csv_content,
            file_name=filename,
            mime="text/csv",
            type="primary",
            use_container_width=True
        )
    
    # Preview
    with st.expander("👁️ Preview Export Data", expanded=False):
        df = pd.read_csv(StringIO(csv_content))
        st.dataframe(df.T, use_container_width=True)  # Transpose for better viewing


def export_batch_to_csv(
    batch_results: List[Dict],
    headers: List[str],
    category: str
) -> str:
    """
    Generate CSV content from batch processing results.
    
    Args:
        batch_results: List of dicts, each containing input data and final values
        headers: List of all attribute headers
        category: Product category name
        
    Returns:
        CSV string content
    """
    all_rows = []
    
    for result in batch_results:
        input_data = result.get("input_data", {})
        final_values = result.get("final_values", {})
        
        row_data = {}
        
        # Add input fields
        row_data["sku"] = input_data.get("sku", "")
        row_data["base_code"] = input_data.get("base_code", "")
        row_data["attributes__lulu_ean"] = input_data.get("ean", "")
        row_data["attributes__shipping_weight"] = input_data.get("shipping_weight", "")
        row_data["attributes__color"] = input_data.get("color", "")
        
        # Add extracted values
        for header in headers:
            if header not in row_data:
                row_data[header] = final_values.get(header, "")
        
        all_rows.append(row_data)
    
    df = pd.DataFrame(all_rows)
    
    # Reorder columns
    ordered_columns = [h for h in headers if h in df.columns]
    df = df[ordered_columns]
    
    return df.to_csv(index=False)

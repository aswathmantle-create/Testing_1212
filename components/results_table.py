"""
Results table component with interactive value selection.
"""
import streamlit as st
import pandas as pd
from typing import Dict, List, Optional


def render_results_table(
    extraction_results: Dict[str, Dict[str, str]],
    headers: List[str],
    input_data: dict
) -> Dict[str, str]:
    """
    Render the interactive results table for attribute mapping.
    
    Args:
        extraction_results: Dict with structure {header: {url1: value, url2: value, url3: value}}
        headers: List of attribute headers
        input_data: Original input data from form
        
    Returns:
        Dict mapping header to final selected value
    """
    st.markdown("## 📊 Extraction Results")
    st.markdown("Click on a value to select it for the final output. You can also edit the Final Output directly.")
    
    # Initialize final values in session state if not exists
    if "final_values" not in st.session_state:
        st.session_state.final_values = {}
    
    # Build the data for display
    table_data = []
    
    for header in headers:
        url_values = extraction_results.get(header, {})
        
        row = {
            "Attribute": header,
            "URL 1 Value": url_values.get("url1", ""),
            "URL 2 Value": url_values.get("url2", ""),
            "URL 3 Value": url_values.get("url3", ""),
            "Final Output": st.session_state.final_values.get(header, "")
        }
        table_data.append(row)
    
    # Create DataFrame for display
    df = pd.DataFrame(table_data)
    
    # Render interactive table
    st.markdown("---")
    
    # Table header
    header_cols = st.columns([2, 2, 2, 2, 2.5])
    header_cols[0].markdown("**Attribute Header**")
    header_cols[1].markdown("**URL 1 Value**")
    header_cols[2].markdown("**URL 2 Value**")
    header_cols[3].markdown("**URL 3 Value**")
    header_cols[4].markdown("**Final Output** ✏️")
    
    st.markdown("---")
    
    # Render each row with clickable buttons
    for idx, row in enumerate(table_data):
        cols = st.columns([2, 2, 2, 2, 2.5])
        
        # Attribute name
        cols[0].markdown(f"**{row['Attribute']}**")
        
        # URL 1 Value - clickable
        url1_val = row["URL 1 Value"]
        if url1_val:
            if cols[1].button(
                f"📋 {_truncate(url1_val, 30)}",
                key=f"url1_{idx}",
                help=f"Click to use: {url1_val}"
            ):
                st.session_state.final_values[row["Attribute"]] = url1_val
                st.rerun()
        else:
            cols[1].markdown("*-*")
        
        # URL 2 Value - clickable
        url2_val = row["URL 2 Value"]
        if url2_val:
            if cols[2].button(
                f"📋 {_truncate(url2_val, 30)}",
                key=f"url2_{idx}",
                help=f"Click to use: {url2_val}"
            ):
                st.session_state.final_values[row["Attribute"]] = url2_val
                st.rerun()
        else:
            cols[2].markdown("*-*")
        
        # URL 3 Value - clickable
        url3_val = row["URL 3 Value"]
        if url3_val:
            if cols[3].button(
                f"📋 {_truncate(url3_val, 30)}",
                key=f"url3_{idx}",
                help=f"Click to use: {url3_val}"
            ):
                st.session_state.final_values[row["Attribute"]] = url3_val
                st.rerun()
        else:
            cols[3].markdown("*-*")
        
        # Final Output - editable
        current_final = st.session_state.final_values.get(row["Attribute"], "")
        new_final = cols[4].text_input(
            "Final",
            value=current_final,
            key=f"final_{idx}",
            label_visibility="collapsed"
        )
        
        if new_final != current_final:
            st.session_state.final_values[row["Attribute"]] = new_final
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Auto-fill Best", help="Automatically select the best value for each attribute"):
            _auto_fill_best(extraction_results, headers)
            st.rerun()
    
    with col2:
        if st.button("📋 Use All URL1", help="Use all values from URL 1"):
            for header in headers:
                val = extraction_results.get(header, {}).get("url1", "")
                if val:
                    st.session_state.final_values[header] = val
            st.rerun()
    
    with col3:
        if st.button("🗑️ Clear All", help="Clear all final values"):
            st.session_state.final_values = {}
            st.rerun()
    
    return st.session_state.final_values


def render_results_table_simple(
    extraction_results: Dict[str, Dict[str, str]],
    headers: List[str]
) -> pd.DataFrame:
    """
    Render a simplified view of extraction results as a dataframe.
    
    Args:
        extraction_results: Dict with structure {header: {url1: value, url2: value, url3: value}}
        headers: List of attribute headers
        
    Returns:
        DataFrame with the results
    """
    table_data = []
    
    for header in headers:
        url_values = extraction_results.get(header, {})
        
        row = {
            "Attribute": header,
            "URL 1": url_values.get("url1", ""),
            "URL 2": url_values.get("url2", ""),
            "URL 3": url_values.get("url3", ""),
            "Final": st.session_state.get("final_values", {}).get(header, "")
        }
        table_data.append(row)
    
    df = pd.DataFrame(table_data)
    
    # Display with st.data_editor for editing
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "Attribute": st.column_config.TextColumn("Attribute", disabled=True, width="medium"),
            "URL 1": st.column_config.TextColumn("URL 1 Value", width="medium"),
            "URL 2": st.column_config.TextColumn("URL 2 Value", width="medium"),
            "URL 3": st.column_config.TextColumn("URL 3 Value", width="medium"),
            "Final": st.column_config.TextColumn("Final Output ✏️", width="large")
        },
        hide_index=True,
        key="results_editor"
    )
    
    # Update session state with edited finals
    if "final_values" not in st.session_state:
        st.session_state.final_values = {}
    
    for _, row in edited_df.iterrows():
        st.session_state.final_values[row["Attribute"]] = row["Final"]
    
    return edited_df


def _truncate(text: str, max_length: int) -> str:
    """Truncate text to max length with ellipsis."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def _auto_fill_best(extraction_results: Dict[str, Dict[str, str]], headers: List[str]):
    """
    Auto-fill with the best available value (prioritize URL1, then URL2, then URL3).
    """
    for header in headers:
        url_values = extraction_results.get(header, {})
        
        # Priority: URL1 > URL2 > URL3
        best_value = ""
        for url_key in ["url1", "url2", "url3"]:
            val = url_values.get(url_key, "")
            if val and not best_value:
                best_value = val
                break
        
        if best_value:
            st.session_state.final_values[header] = best_value

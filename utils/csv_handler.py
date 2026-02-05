"""
CSV handling utilities for import and export.
"""
import pandas as pd
from typing import List, Dict, Optional
from io import StringIO, BytesIO


def parse_csv(file_content, encoding: str = "utf-8") -> pd.DataFrame:
    """
    Parse CSV file content into DataFrame.
    
    Args:
        file_content: File content (string, bytes, or file-like object)
        encoding: Character encoding
        
    Returns:
        pandas DataFrame
    """
    try:
        if isinstance(file_content, bytes):
            file_content = file_content.decode(encoding)
        
        if isinstance(file_content, str):
            df = pd.read_csv(StringIO(file_content))
        else:
            df = pd.read_csv(file_content)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        return df
        
    except Exception as e:
        raise ValueError(f"Failed to parse CSV: {str(e)}")


def generate_csv(
    data: List[Dict],
    columns: Optional[List[str]] = None,
    include_index: bool = False
) -> str:
    """
    Generate CSV string from list of dictionaries.
    
    Args:
        data: List of row dictionaries
        columns: Optional list of columns in order
        include_index: Whether to include row index
        
    Returns:
        CSV string
    """
    df = pd.DataFrame(data)
    
    if columns:
        # Reorder columns, adding missing ones with empty values
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        df = df[[col for col in columns if col in df.columns]]
    
    return df.to_csv(index=include_index)


def generate_csv_bytes(
    data: List[Dict],
    columns: Optional[List[str]] = None,
    include_index: bool = False
) -> bytes:
    """
    Generate CSV as bytes for download.
    
    Args:
        data: List of row dictionaries
        columns: Optional list of columns in order
        include_index: Whether to include row index
        
    Returns:
        CSV bytes
    """
    csv_str = generate_csv(data, columns, include_index)
    return csv_str.encode("utf-8")


def merge_input_and_extracted(
    input_data: Dict,
    extracted_data: Dict[str, str],
    all_headers: List[str]
) -> Dict[str, str]:
    """
    Merge input data with extracted data into a single row.
    
    Args:
        input_data: User input data (sku, base_code, etc.)
        extracted_data: Extracted attribute values
        all_headers: Complete list of headers
        
    Returns:
        Merged dictionary with all headers
    """
    result = {}
    
    # Map input fields to their header names
    input_mapping = {
        "sku": "sku",
        "base_code": "base_code",
        "ean": "attributes__lulu_ean",
        "shipping_weight": "attributes__shipping_weight",
        "color": "attributes__color",
        "product_type": "attributes__product_type"
    }
    
    # Add all headers with empty default
    for header in all_headers:
        result[header] = ""
    
    # Add input data
    for input_key, header_name in input_mapping.items():
        if input_key in input_data and header_name in result:
            result[header_name] = input_data[input_key]
    
    # Add extracted data (won't overwrite input data)
    for header, value in extracted_data.items():
        if header in result and not result[header]:
            result[header] = value
    
    return result


def create_template_csv(headers: List[str], sample_rows: int = 2) -> str:
    """
    Create a template CSV with headers and empty sample rows.
    
    Args:
        headers: List of column headers
        sample_rows: Number of empty sample rows
        
    Returns:
        CSV string
    """
    data = []
    for _ in range(sample_rows):
        data.append({h: "" for h in headers})
    
    return generate_csv(data, headers)

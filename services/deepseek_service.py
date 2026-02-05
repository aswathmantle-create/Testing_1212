"""
DeepSeek API service for extracting attributes from markdown content.
"""
import json
from typing import Optional, Callable, List
from openai import OpenAI
from config.settings import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from config.categories import get_category_mapping_prompts


class DeepSeekService:
    """Service for extracting product attributes using DeepSeek API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.client = None
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=DEEPSEEK_BASE_URL
            )
    
    def extract_attributes(
        self, 
        markdown_content: str, 
        headers: List[str],
        category: str,
        log_callback: Optional[Callable] = None,
        mm43_context: str = ""
    ) -> dict:
        """
        Extract attribute values from markdown content based on headers.
        
        Args:
            markdown_content: The scraped markdown content
            headers: List of attribute headers to extract
            category: The product category
            log_callback: Optional callback function for logging
            mm43_context: Optional MM43 product data for improved accuracy
            
        Returns:
            dict mapping header to extracted value
        """
        if not self.client:
            if log_callback:
                log_callback("❌ DeepSeek: API key not configured")
            return {h: "" for h in headers}
            
        if not markdown_content:
            if log_callback:
                log_callback("⚠️ DeepSeek: No content to process")
            return {h: "" for h in headers}
            
        if log_callback:
            log_callback(f"🤖 DeepSeek: Extracting {len(headers)} attributes for {category}")
        
        # Get category-specific mapping prompts
        mapping_prompts = get_category_mapping_prompts(category)
        has_mapping = len(mapping_prompts) > 0
        
        if has_mapping and log_callback:
            log_callback(f"   📋 Using category-specific mapping rules ({len(mapping_prompts)} rules)")
            
        # Build the extraction prompt with mapping instructions
        if has_mapping:
            # Build detailed attribute list with mapping rules
            headers_with_rules = []
            for h in headers:
                rule = mapping_prompts.get(h, "Extract from data")
                headers_with_rules.append(f"- {h}: {rule}")
            headers_list = "\n".join(headers_with_rules)
        else:
            headers_list = "\n".join([f"- {h}" for h in headers])
        
        # Include MM43 context if provided
        mm43_section = ""
        if mm43_context:
            mm43_section = f"""
ADDITIONAL PRODUCT CONTEXT (MM43 Data):
{mm43_context[:3000]}

Use this MM43 data to help identify and validate product attributes.
"""
        
        # Enhanced system prompt with mapping awareness
        if has_mapping:
            system_prompt = """You are a product data extraction and content creation specialist.
Your task is to extract and FORMAT product data according to specific rules.

IMPORTANT RULES:
1. For "Passthrough" attributes: Extract exactly as found in the data
2. For "From Data" attributes: Find and extract the value from the content
3. For formatted attributes (name, title): Follow the exact format specified
4. For bullet points: Create SHORT sentences (max 75 characters) highlighting key features
5. For product description: Write unique, engaging content without copying
6. For keywords: Generate relevant SEO keywords separated by commas
7. For "Leave empty" attributes: Return empty string ""

Return ONLY a valid JSON object with the exact attribute names as keys.
If a value cannot be found, use an empty string "".
Do not include any explanation, just the JSON object."""
        else:
            system_prompt = """You are a product data extraction specialist. 
Extract product attribute values from the provided content accurately.
Return ONLY a valid JSON object with the exact attribute names as keys.
If a value cannot be found, use an empty string "".
Do not include any explanation, just the JSON object."""

        user_prompt = f"""Product Category: {category}
{mm43_section}
Extract and format values for these attributes following the specified rules:
{headers_list}

Content to extract from:
{markdown_content[:15000]}

Return a JSON object with attribute names as keys and properly formatted values.
Example format:
{{"attributes__brand": "Samsung", "attributes__model": "Galaxy S24", ...}}"""

        try:
            if log_callback:
                log_callback("   Sending request to DeepSeek API...")
                
            response = self.client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON from response
            # Handle cases where response might have markdown code blocks
            if result_text.startswith("```"):
                # Extract JSON from code block
                lines = result_text.split("\n")
                json_lines = []
                in_json = False
                for line in lines:
                    if line.startswith("```") and not in_json:
                        in_json = True
                        continue
                    elif line.startswith("```") and in_json:
                        break
                    elif in_json:
                        json_lines.append(line)
                result_text = "\n".join(json_lines)
            
            try:
                extracted_data = json.loads(result_text)
                if log_callback:
                    log_callback(f"✅ DeepSeek: Successfully extracted {len(extracted_data)} attributes")
                
                # Ensure all headers are in response
                result = {}
                for h in headers:
                    result[h] = extracted_data.get(h, "")
                return result
                
            except json.JSONDecodeError as e:
                if log_callback:
                    log_callback(f"⚠️ DeepSeek: JSON parse error - {str(e)}")
                    log_callback(f"   Raw response: {result_text[:200]}...")
                return {h: "" for h in headers}
                
        except Exception as e:
            if log_callback:
                log_callback(f"❌ DeepSeek: API error - {str(e)}")
            return {h: "" for h in headers}
    
    def extract_from_multiple_sources(
        self,
        markdown_contents: dict,
        headers: List[str],
        category: str,
        log_callback: Optional[Callable] = None,
        mm43_context: str = ""
    ) -> dict:
        """
        Extract attributes from multiple markdown sources (url1, url2, url3, pdf).
        
        Args:
            markdown_contents: dict with keys like 'url1', 'url2', 'url3', 'pdf' 
                              and values containing markdown content
            headers: List of attribute headers to extract
            category: The product category
            log_callback: Optional callback function for logging
            mm43_context: Optional MM43 product data for improved accuracy
            
        Returns:
            dict with structure: {header: {url1: value, url2: value, url3: value, pdf: value}}
        """
        results = {h: {} for h in headers}
        
        for url_key, content_data in markdown_contents.items():
            if content_data.get("success") and content_data.get("markdown"):
                if log_callback:
                    source_label = "PDF" if url_key == "pdf" else url_key.upper()
                    log_callback(f"\n📊 Processing {source_label}...")
                    
                extracted = self.extract_attributes(
                    content_data["markdown"],
                    headers,
                    category,
                    log_callback,
                    mm43_context=mm43_context
                )
                
                for h in headers:
                    results[h][url_key] = extracted.get(h, "")
            else:
                if log_callback:
                    log_callback(f"⚠️ Skipping {url_key} - no content available")
                for h in headers:
                    results[h][url_key] = ""
                    
        return results

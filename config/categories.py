"""
Category-specific attribute headers for CMS template generator.
Each category contains the exact column headers as provided.
"""

# Default input fields that are always required (category-agnostic)
DEFAULT_INPUT_FIELDS = [
    "sku",
    "base_code",
    "ean",
    "shipping_weight",
    "color",
    "product_type",
    "url1",
    "url2",
    "url3"
]

# Category-specific attribute headers
CATEGORIES = {
    "TV": {
        "name": "TV",
        "headers": [
            "sku", "base_code", "attributes__lulu_ean", "attributes__keywords",
            "attributes__shipping_weight", "attributes__brand", "sap des", "mm43",
            "link", "Status", "name", "attributes__product_title",
            "attributes__bullet_point_1", "attributes__bullet_point_2", "attributes__bullet_point_3",
            "attributes__bullet_point_4", "attributes__bullet_point_5", "attributes__bullet_point_6",
            "attributes__product_description", "attributes__lulu_product_type", "attributes__model",
            "attributes__weight", "attributes__product_dimensions", "attributes__package_dimensions",
            "attributes__os", "attributes__os_version", "attributes__internal _storage",
            "attributes__display_type", "attributes__display_feature", "attributes__display_resolution",
            "attributes__bluetooth", "attributes__screen_size", "attributes__refresh_rate",
            "attributes__hdmi", "attributes__usb", "attributes__ports", "attributes__features",
            "attributes__no_of_channels", "attributes__color", "attributes__supported_video_formats",
            "attributes__other_information", "attributes__audio", "attributes__model_year",
            "attributes__wifi", "attributes__voltage", "attributes__frequency_range",
            "attributes__power_consumption", "attributes__cord_length", "attributes__processor",
            "attributes__processor_version", "attributes__mounting_type"
        ]
    },
    
    "Vacuum Cleaner": {
        "name": "Vacuum Cleaner",
        "headers": [
            "sku", "base_code", "attributes__lulu_ean", "attributes__shipping_weight",
            "attributes__keywords", "name", "attributes__product_title",
            "attributes__bullet_point_1", "attributes__bullet_point_2", "attributes__bullet_point_3",
            "attributes__bullet_point_4", "attributes__bullet_point_5", "attributes__bullet_point_6",
            "attributes__product_description", "attributes__brand", "attributes__product_type",
            "attributes__model", "attributes__model_year", "attributes__material", "attributes__color",
            "attributes__product_dimensions", "attributes__weight", "attributes__accessories",
            "attributes__in_the_box", "attributes__country_of_origin", "attributes__wattage",
            "attributes__voltage", "attributes__power_consumption", "attributes__suction_power",
            "attributes__battery_capacity", "attributes__battery_type", "attributes__battery_life",
            "attributes__charging_type", "attributes__charging_time", "attributes__runtime",
            "attributes__capacity", "attributes__tank_capacity", "attributes__sensors",
            "attributes__iot_conncectivity", "attributes__cord_length", "attributes__filter",
            "attributes__no_of_speed_settings", "attributes__features", "attributes__other_information"
        ]
    },
    
    "Smartphone": {
        "name": "Smartphone",
        "headers": [
            "sku", "base_code", "attributes__lulu_ean", "attributes__shipping_weight",
            "attributes__keywords", "attributes__brand", "name", "attributes__product_title",
            "attributes__bullet_point_1", "attributes__bullet_point_2", "attributes__bullet_point_3",
            "attributes__bullet_point_4", "attributes__bullet_point_5", "attributes__bullet_point_6",
            "attributes__product_description", "attributes__product_type", "attributes__model",
            "attributes__model_year", "attributes__color", "attributes__weight",
            "attributes__product_dimensions", "attributes__material", "attributes__ip_rating",
            "attributes__in_the_box", "attributes__country_of_origin", "attributes__screen_size",
            "attributes__display_type", "attributes__display_resolution", "attributes__brightness",
            "attributes__refresh_rate", "attributes__os", "attributes__os_version",
            "attributes__processor", "attributes__version", "attributes__gpu", "attributes__ram",
            "attributes__storage_type", "attributes__internal_storage", "attributes__external_storage",
            "attributes__camera_features", "attributes__camera_resolution", "attributes__primary_camera",
            "attributes__secondary_camera", "attributes__video_recording", "attributes__flash",
            "attributes__network", "attributes__sim", "attributes__bluetooth", "attributes__wifi",
            "attributes__nfc", "attributes__usb", "attributes__ports", "attributes__sensors",
            "attributes__charging_speed", "attributes__battery_capacity", "attributes__battery_type",
            "attributes__battery_life", "attributes__charging_type", "attributes__audio",
            "attributes__special_features", "attributes__other_information"
        ]
    },
    
    "Elec-LA-Refrigerators": {
        "name": "Refrigerators",
        "headers": [
            "sku", "base_code", "attributes__lulu_ean", "attributes__keywords",
            "attributes__shipping_weight", "name", "attributes__product_title",
            "attributes__bullet_point_1", "attributes__bullet_point_2", "attributes__bullet_point_3",
            "attributes__bullet_point_4", "attributes__bullet_point_5", "attributes__bullet_point_6",
            "attributes__product_description", "attributes___brand", "attributes___lulu_product_type",
            "attributes__model", "attributes__color", "attributes__finish",
            "attributes__product_dimensions", "attributes__weight", "attributes__installation",
            "attributes__in_the_box", "attributes__country_of_origin", "attributes___material",
            "attributes__gross_capacity", "attributes__net_capacity", "attributes___capacity",
            "attributes__freezer_capacity", "attributes__type_of_defrost", "attributes__climate_class",
            "attributes__compressor", "attributes__cooling_technology", "attributes__refrigerant",
            "attributes__wattage", "attributes__voltage", "attributes__frequency_range",
            "attributes__power_consumption", "attribute__no_of_shelves", "attribute__no_of_drawers",
            "attribute__bottle_holder", "attributes__icemaker", "attributes__door_handle_type",
            "attributes___display_type", "attributes__iot_connectivity", "attributes__sensors",
            "attributes__special_features", "attributes__features", "attributes__other_information"
        ]
    },
    
    "Elec-LA-Air Conditioners": {
        "name": "Air Conditioners",
        "headers": [
            "sku", "base_code", "attributes__lulu_ean", "attributes__shipping_weight",
            "attributes__keywords", "attributes__brand", "name", "attributes__product_title",
            "attributes__bullet_point_1", "attributes__bullet_point_2", "attributes__bullet_point_3",
            "attributes__bullet_point_4", "attributes__bullet_point_5", "attributes__bullet_point_6",
            "attributes__product_description", "attributes__lulu_product_type", "attributes__model",
            "attributes__color", "attributes__material", "attributes__features",
            "attributes__other information", "attributes__country of origin", "attributes__note",
            "attributes__in the box", "attributes__capacity", "attributes__cooling capacity",
            "attributes__wattage", "attributes__voltage", "attributes__power_consumption",
            "attributes__refrigerant", "attributes__moisture removal", "attributes__climate class",
            "attributes__compressor", "attributes__compressor warranty", "attributes__iot connectivity",
            "attributes__product dimensions", "attributes__indoor unit dimensions",
            "attributes__outdoor unit dimensions", "attributes__weight", "attributes__indoor unit weight",
            "attributes__outdoor unit weight", "attributes__noise level", "attributes__indoor noise level",
            "attributes__outdoor noise level", "attributes__air swing", "attributes__filter"
        ]
    },
    
    "Elec-LA-Washing Machines": {
        "name": "Washing Machines",
        "headers": [
            "sku", "base_code", "attributes__lulu_ean", "attributes__shipping_weight",
            "attributes__keywords", "attributes__brand", "name", "attributes__product_title",
            "attributes__bullet_point_1", "attributes__bullet_point_2", "attributes__bullet_point_3",
            "attributes__bullet_point_4", "attributes__bullet_point_5", "attributes__bullet_point_6",
            "attributes__product_description", "attributes__lulu_product_type", "attributes__model",
            "attributes__material", "attributes__color", "attributes__weight",
            "attributes__country_of_origin", "attributes__product_dimensions",
            "attributes__package_dimensions", "attributes__capacity", "attributes__washer_capacity",
            "attributes__dryer_capacity", "attributes__spin_speed", "attributes__water_consumption",
            "attributes__noise_level", "attributes__programs", "attributes__no_of_programs",
            "attributes__wash_programmes", "attributes__special_features", "attributes__features",
            "attributes__display_type", "attributes__iot_connectivity", "attributes__installation",
            "attributes__other_information", "attributes__in_the_box", "attributes__motor_warranty"
        ]
    },
    
    "Elec-C&A-Laptops": {
        "name": "Laptops",
        "headers": [
            "sku", "base_code", "attributes__lulu_ean", "attributes__shipping_weight",
            "attributes__keywords", "attributes__brand", "name", "attributes__product_title",
            "attributes__bullet_point_1", "attributes__bullet_point_2", "attributes__bullet_point_3",
            "attributes__bullet_point_4", "attributes__bullet_point_5", "attributes__bullet_point_6",
            "attributes__product_description", "attributes__lulu_product_type", "attributes__model",
            "attributes__part_number", "attributes__model_year", "attributes__color",
            "attributes__weight", "attributes__product_dimensions", "attributes__in_the_box",
            "attributes__country_of_origin", "attributes__accessories", "attributes__screen_size",
            "attributes__display_type", "attributes__display_feature", "attributes__refresh_rate",
            "attributes__display_resolution", "attributes__brightness", "attributes__processor",
            "attributes__version", "attributes__ram", "attributes__storage", "attributes__hdd",
            "attributes__ssd", "attributes__graphics", "attributes__graphic_memory",
            "attributes__graphics_card", "attributes__os", "attributes__os_version",
            "attributes__wifi", "attributes__bluetooth", "attributes__usb", "attributes__hdmi",
            "attributes__ports", "attributes__ethernet", "attributes__battery_capacity",
            "attributes__battery_type", "attributes__battery_life", "attributes__power",
            "attributes__mic", "attributes__audio", "attributes__web_camera",
            "attributes__keyboard_&_touchpad", "attributes__features", "attributes__other_information"
        ]
    },
    
    "Elec-Audio-Headphones": {
        "name": "Headphones",
        "headers": [
            "sku", "base_code", "attributes__lulu_ean", "attributes__shipping_weight",
            "attributes__brand", "name", "attributes__product_title",
            "attributes__bullet_point_1", "attributes__bullet_point_2", "attributes__bullet_point_3",
            "attributes__bullet_point_4", "attributes__bullet_point_5", "attributes__bullet_point_6",
            "attributes__product_description", "attributes__lulu_product_type", "attributes__model",
            "attributes__weight", "attributes__in_the_box", "attributes__product_dimensions",
            "attributes__design", "attributes__connectivity", "attributes__mic",
            "attributes__microphone_type", "attributes__noise_cancellation",
            "attributes__country_of_origin", "attributes__color", "attributes__battery_type",
            "attributes__charging_time", "attributes__water_resistance", "attributes__battery_life",
            "attributes__driver_unit", "attributes__ip_rating", "attributes__features",
            "attributes__noise_level", "attributes__cable_length", "attributes__other_information",
            "attributes__bluetooth", "attributes__battery_capacity", "attributes__keywords",
            "attributes__stand_by_time", "attributes__range"
        ],
        "mapping_prompts": {
            "sku": "Passthrough - use the value provided by user",
            "base_code": "Passthrough - use the value provided by user",
            "attributes__lulu_ean": "Passthrough - use the value provided by user",
            "attributes__shipping_weight": "Passthrough - use the value provided by user",
            "attributes__brand": "Passthrough - extract the brand name exactly as found",
            "name": "Create product name in format: Brand + Series + Design Type + Product Type, Feature, Color, Model Number",
            "attributes__product_title": "Same as 'name' field - Brand + Series + Design Type + Product Type, Feature, Color, Model Number",
            "attributes__bullet_point_1": "A short 75 character sentence starting with a key product attribute/feature",
            "attributes__bullet_point_2": "A short 75 character sentence starting with a key product attribute/feature",
            "attributes__bullet_point_3": "A short 75 character sentence starting with a key product attribute/feature",
            "attributes__bullet_point_4": "A short 75 character sentence starting with a key product attribute/feature",
            "attributes__bullet_point_5": "A short 75 character sentence starting with a key product attribute/feature",
            "attributes__bullet_point_6": "Leave empty",
            "attributes__product_description": "Write a unique 200-word product description without plagiarism, based on the extracted data",
            "attributes__lulu_product_type": "Passthrough - use the product type category",
            "attributes__model": "Extract exact model name/number from data",
            "attributes__weight": "Extract weight with unit from data",
            "attributes__in_the_box": "Extract box contents/accessories from data",
            "attributes__product_dimensions": "Extract dimensions from data",
            "attributes__design": "Extract design type (Over-ear, On-ear, In-ear, etc.) from data",
            "attributes__connectivity": "Extract connectivity type (Wireless, Wired, Bluetooth, etc.) from data",
            "attributes__mic": "Extract microphone info (Yes/No/Built-in) from data",
            "attributes__microphone_type": "Extract microphone type from data",
            "attributes__noise_cancellation": "Extract noise cancellation feature (Active/Passive/None) from data",
            "attributes__country_of_origin": "Extract country of origin from data",
            "attributes__color": "Extract color from data",
            "attributes__battery_type": "Extract battery type from data",
            "attributes__charging_time": "Extract charging time from data",
            "attributes__water_resistance": "Extract water resistance rating from data",
            "attributes__battery_life": "Extract battery life/playback time from data",
            "attributes__driver_unit": "Extract driver size/unit from data",
            "attributes__ip_rating": "Extract IP rating from data",
            "attributes__features": "Extract key features as comma-separated list from data",
            "attributes__noise_level": "Extract noise level from data",
            "attributes__cable_length": "Extract cable length from data",
            "attributes__other_information": "Extract any other relevant information from data",
            "attributes__bluetooth": "Extract Bluetooth version from data",
            "attributes__battery_capacity": "Extract battery capacity (mAh) from data",
            "attributes__keywords": "Generate relevant SEO keywords separated by commas",
            "attributes__stand_by_time": "Extract standby time from data",
            "attributes__range": "Extract wireless range from data"
        }
    },
    
    "Elec-M&W-Smartphones & Tablets": {
        "name": "Smartphones & Tablets",
        "headers": [
            "sku", "base_code", "attributes__lulu_ean", "attributes__shipping_weight",
            "attributes__keywords", "attributes__brand", "name", "attributes__product_title",
            "attributes__bullet_point_1", "attributes__bullet_point_2", "attributes__bullet_point_3",
            "attributes__bullet_point_4", "attributes__bullet_point_5", "attributes__bullet_point_6",
            "attributes__product_description", "attributes__lulu_product_type", "attributes__model",
            "attributes__model_year", "attributes__color", "attributes__weight",
            "attributes__product_dimensions", "attributes__material", "attributes__ip_rating",
            "attributes__in_the_box", "attributes__country_of_origin", "attributes__screen_size",
            "attributes__display_type", "attributes__display_resolution", "attributes__brightness",
            "attributes__refresh_rate", "attributes__os", "attributes__os_version",
            "attributes__processor", "attributes__version", "attributes__gpu", "attributes__ram",
            "attributes__storage_type", "attributes__internal_storage", "attributes__external_storage",
            "attributes__camera_features", "attributes__camera_resolution", "attributes__primary_camera",
            "attributes__secondary_camera", "attributes__video_recording", "attributes__flash",
            "attributes__network", "attributes__sim", "attributes__bluetooth", "attributes__wifi",
            "attributes__nfc", "attributes__usb", "attributes__ports", "attributes__sensors",
            "attributes__charging_speed", "attributes__battery_capacity", "attributes__battery_type",
            "attributes__battery_life", "attributes__charging_type", "attributes__audio",
            "attributes__special_features", "attributes__other_information"
        ]
    }
}

def get_category_names() -> list:
    """Return list of category names."""
    return list(CATEGORIES.keys())

def get_category_headers(category: str) -> list:
    """Return attribute headers for a specific category."""
    if category in CATEGORIES:
        return CATEGORIES[category]["headers"]
    return []

def get_category_mapping_prompts(category: str) -> dict:
    """Return mapping prompts for a specific category."""
    if category in CATEGORIES:
        return CATEGORIES[category].get("mapping_prompts", {})
    return {}

def get_extraction_headers(category: str) -> list:
    """
    Return headers that need to be extracted from URLs.
    Excludes the default input fields that user provides.
    """
    all_headers = get_category_headers(category)
    # Exclude headers that are provided by user input
    exclude_set = {"sku", "base_code", "attributes__lulu_ean", "attributes__shipping_weight"}
    return [h for h in all_headers if h not in exclude_set]

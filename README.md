# 🏭 CMS Template Generator

A maximalist Streamlit web application for generating CMS product templates across multiple categories.

## Features

- **Multi-Category Support**: TV, Smartphone, Refrigerators, Air Conditioners, Washing Machines, Laptops
- **Dual Processing Modes**: Single SKU or Batch CSV upload
- **URL Scraping**: Firecrawl API integration for converting product pages to markdown
- **AI-Powered Extraction**: DeepSeek API for intelligent attribute mapping
- **Interactive Results Table**: Click-to-select values from multiple sources
- **Real-time Console**: Monitor backend operations live
- **CSV Export**: Download final mapped templates

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your keys:
```
FIRECRAWL_API_KEY=your_firecrawl_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
```

### 3. Run the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Usage

1. **Select Category** - Choose the product category from the sidebar
2. **Choose Mode** - Single SKU for one product, or Batch for CSV upload
3. **Enter Details** - Fill in product information and URLs
4. **Map & Extract** - Click to scrape URLs and extract attributes
5. **Review Results** - Click values to select, or edit manually
6. **Export** - Download the final CSV template

## Project Structure

```
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
│
├── config/
│   ├── categories.py     # Category definitions & headers
│   └── settings.py       # App settings & API config
│
├── services/
│   ├── firecrawl_service.py  # URL scraping service
│   └── deepseek_service.py   # AI extraction service
│
├── components/
│   ├── sidebar.py        # Sidebar UI
│   ├── input_form.py     # Input forms
│   ├── results_table.py  # Interactive results
│   ├── console.py        # Console logger
│   └── export.py         # CSV export
│
└── utils/
    ├── validators.py     # Input validation
    └── csv_handler.py    # CSV utilities
```

## Supported Categories

| Category | Attributes |
|----------|------------|
| TV | 38 attributes |
| Smartphone | 60 attributes |
| Refrigerators | 48 attributes |
| Air Conditioners | 46 attributes |
| Washing Machines | 40 attributes |
| Laptops | 56 attributes |

## API Requirements

- **Firecrawl**: Get API key from [firecrawl.dev](https://firecrawl.dev)
- **DeepSeek**: Get API key from [platform.deepseek.com](https://platform.deepseek.com)

## License

MIT License

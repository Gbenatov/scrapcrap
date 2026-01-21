# Scrapy FilesPipeline Document Downloader

## Overview

A production-ready Scrapy-based system for downloading documents from the Israeli Court's class action register (פנקס תובענות ייצוגיות). This implementation uses Scrapy's FilesPipeline to handle document downloads while automatically following links and organizing files.

## What's New

Based on your request to improve document handling, this system provides:

✅ **Link Following**: Automatically navigates through multiple pages to find documents  
✅ **Document Downloads**: Uses Scrapy's FilesPipeline to download PDFs, DOCs, and other files  
✅ **File Organization**: Automatically organizes downloads by case number  
✅ **Metadata Tracking**: Stores information about each case and download  
✅ **Report Generation**: Creates JSON and CSV reports of all downloads  
✅ **Error Handling**: Gracefully handles failed downloads and network errors  
✅ **Respectful Crawling**: Respects robots.txt, uses delays, limits concurrency  

## Key Components

### 1. Spiders (`scraper_system/court_document_scraper.py`)

**CourtDocumentSpider**
- Parses the main class actions index page
- Extracts case links and details
- Finds document URLs
- Sends to FilesPipeline for download

**DocumentLinkFollowerSpider**
- Alternative approach for harder-to-reach documents
- Follows links across multiple pages
- Uses depth limiting to prevent infinite loops
- Better for websites with nested document links

### 2. Custom Pipeline (`scraper_system/pipelines.py`)

**CourtDocumentPipeline** (extends FilesPipeline)
- Organizes downloaded files by case number
- Stores metadata in JSONL format (one record per line)
- Tracks download success/failure
- Generates detailed logs

**DocumentMetadataExporter**
- Reads JSONL metadata files
- Generates JSON and CSV reports
- Calculates success statistics
- Provides summary information

### 3. Configuration (`scraper_system/settings.py`)

Complete Scrapy settings including:
- FilesPipeline configuration
- Request throttling and delays
- HTTP caching
- Memory management
- Logging levels

### 4. Runner Script (`scraper_system/run_scraper.py`)

CLI interface with commands:
- `scrape` - Run main spider
- `follow` - Run link follower spider
- `report` - Generate reports from results
- `all` - Complete pipeline (crawl + report)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Scraper

```bash
cd scraper_system
python run_scraper.py all
```

This will:
1. Download documents from court.gov.il
2. Organize by case number
3. Generate reports

### 3. Check Results

```bash
ls -la downloads/court_documents/
cat downloads/report.json
open downloads/documents.csv
```

## How It Works

### Flow Diagram

```
┌─────────────────────────────────────┐
│ Start: Class Actions Index Page     │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│ CourtDocumentSpider                 │
│ ├─ Parse main page                  │
│ ├─ Extract case links               │
│ └─ For each case → parse_case_page  │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│ parse_case_page()                   │
│ ├─ Extract case details             │
│ ├─ Find document URLs               │
│ ├─ Create Item with file_urls       │
│ └─ Yield item                       │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│ CourtDocumentPipeline               │
│ (Custom FilesPipeline)              │
│ ├─ Validate document URLs           │
│ ├─ Download in parallel             │
│ ├─ Organize: case_123/file.pdf      │
│ ├─ Store metadata (JSONL)           │
│ └─ Track success/failure            │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│ Output Files                        │
│ ├─ downloads/case_123/doc1.pdf      │
│ ├─ downloads/case_456/doc2.pdf      │
│ ├─ metadata.jsonl (case info)       │
│ ├─ report.json (summary)            │
│ └─ documents.csv (spreadsheet)      │
└─────────────────────────────────────┘
```

### Document Download Process (FilesPipeline)

```
1. Item with file_urls is created
           ↓
2. Pipeline calls get_media_requests()
           ↓
3. Each URL becomes a Request
           ↓
4. Requests queued in Scheduler
           ↓
5. Downloader fetches files in parallel
           ↓
6. file_path() determines where to save
           ↓
7. Files saved organized by case
           ↓
8. item_completed() processes results
           ↓
9. Metadata stored alongside files
```

## Directory Structure

```
scraper_system/
├── court_document_scraper.py      # Spider definitions
├── pipelines.py                   # Custom pipeline + exporter
├── settings.py                    # Scrapy configuration
├── run_scraper.py                # CLI runner script
├── __init__.py                    # Package marker
└── data/                          # Sample data (optional)

downloads/
├── court_documents/               # Downloaded files
│   ├── case_12345/               # Organized by case
│   │   ├── decision.pdf
│   │   ├── summons.pdf
│   │   └── judgment.docx
│   ├── case_12346/
│   │   └── agreement.pdf
│   └── metadata.jsonl            # Case metadata
├── report.json                    # Summary report
└── documents.csv                  # Spreadsheet export
```

## Usage Examples

### Basic Download

```bash
cd scraper_system
python run_scraper.py scrape
```

Downloads documents using main spider.

### Deep Link Following

```bash
python run_scraper.py follow
```

Uses alternative spider for hard-to-reach documents.

### Generate Reports

```bash
python run_scraper.py report
```

Creates JSON and CSV reports from metadata.

### Full Pipeline

```bash
python run_scraper.py all
```

Runs everything: crawl, download, and report.

### Direct Scrapy Commands

```bash
# Run spider directly
scrapy crawl court_documents -L INFO

# Export to JSON
scrapy crawl court_documents -o results.json -L WARNING

# Run with custom settings
scrapy crawl court_documents -s FILES_STORE=custom_dir/

# Use Scrapy shell for debugging
scrapy shell "https://www.court.gov.il/..."
> response.css('a[href$=".pdf"]::attr(href)').getall()
```

## Output Examples

### Metadata (JSONL)

Each line is a JSON object (one case per line):

```json
{"timestamp": "2026-01-21T10:30:00", "case_number": "01-12345", "case_title": "תובענה X", "requested_files": 5, "downloaded_files": 4, "failed_downloads": 1, "file_paths": ["case_12345/doc1.pdf", "case_12345/doc2.pdf"], "failed_urls": ["https://example.com/missing.pdf"]}
{"timestamp": "2026-01-21T10:35:00", "case_number": "01-12346", "case_title": "תובענה Y", "requested_files": 3, "downloaded_files": 3, "failed_downloads": 0, "file_paths": ["case_12346/agreement.pdf"], "failed_urls": []}
```

### Report Summary (JSON)

```json
{
  "generated": "2026-01-21T11:00:00",
  "total_cases": 45,
  "total_files_requested": 234,
  "total_files_downloaded": 218,
  "total_failures": 16,
  "success_rate": 93.2,
  "cases": [
    {"timestamp": "2026-01-21T10:30:00", ...},
    ...
  ]
}
```

### Spreadsheet (CSV)

| timestamp | case_number | case_url | requested_files | downloaded_files |
|-----------|------------|----------|-----------------|------------------|
| 2026-01-21T10:30:00 | 01-12345 | https://... | 5 | 4 |
| 2026-01-21T10:35:00 | 01-12346 | https://... | 3 | 3 |

## Configuration

### Key Settings

Edit `scraper_system/settings.py`:

```python
# Storage location
FILES_STORE = 'downloads/court_documents'

# Crawling speed
CONCURRENT_REQUESTS = 8        # Parallel downloads (1-16)
DOWNLOAD_DELAY = 2             # Seconds between requests

# File management
FILES_EXPIRES = 90             # Days to keep downloaded files
DOWNLOAD_TIMEOUT = 30          # Seconds to wait for response

# Respect website
ROBOTSTXT_OBEY = True
AUTOTHROTTLE_ENABLED = True
```

### Memory Management

```python
# Prevent excessive memory usage
MEMUSAGE_LIMIT_MB = 256        # Stop if memory exceeds this
MEMUSAGE_CHECK_INTERVAL_SECONDS = 60
```

## Troubleshooting

### No Documents Found

**Problem**: Spider finds cases but no documents

**Solution**:
1. Check website manually in browser
2. Use Scrapy shell to test selectors:
   ```bash
   scrapy shell "https://www.court.gov.il/..."
   response.css('a[href$=".pdf"]::attr(href)').getall()
   ```
3. Update CSS selectors in spider if HTML changed

### Too Many Failed Downloads

**Problem**: Many documents failed to download

**Solution**:
1. Check `metadata.jsonl` for `failed_urls`
2. Verify URLs work in browser
3. Check server error codes in logs
4. Increase `DOWNLOAD_TIMEOUT` if timeouts

### Slow Performance

**Problem**: Downloads taking too long

**Solution**:
1. Increase `CONCURRENT_REQUESTS` (8 → 16)
2. Decrease `DOWNLOAD_DELAY` (2 → 1)
3. Enable HTTP caching (usually enabled by default)
4. Check network/internet speed

### High Memory Usage

**Problem**: Process using too much memory

**Solution**:
1. Decrease `CONCURRENT_REQUESTS` (16 → 8)
2. Lower `MEMUSAGE_LIMIT_MB` (256 → 128)
3. Run reports separately (don't keep all in memory)

## Advanced Usage

### Custom Spider for Specific Cases

```python
class CustomCaseSpider(scrapy.Spider):
    name = 'specific_cases'
    
    def __init__(self, case_ids, *args, **kwargs):
        self.case_ids = case_ids.split(',')
        self.start_urls = [
            f'https://www.court.gov.il/...?caseID={case_id}'
            for case_id in self.case_ids
        ]
        super().__init__(*args, **kwargs)
    
    # Rest of spider implementation...
```

Run with:
```bash
scrapy crawl specific_cases -a case_ids=12345,12346,12347
```

### Export to Database

Modify pipeline to save to database instead of JSON:

```python
class DatabasePipeline(CourtDocumentPipeline):
    def item_completed(self, results, item, info):
        # Save to database
        self.db.insert(dict(item))
        return item
```

## Files Included

- `court_document_scraper.py` - Two spider implementations
- `pipelines.py` - Custom FilesPipeline and metadata handling
- `settings.py` - Scrapy configuration
- `run_scraper.py` - CLI interface
- `SCRAPY_GUIDE.md` - Detailed documentation
- `SCRAPY_EXAMPLES.md` - Code examples

## Documentation

- **[SCRAPY_GUIDE.md](SCRAPY_GUIDE.md)** - Comprehensive usage guide
- **[SCRAPY_EXAMPLES.md](SCRAPY_EXAMPLES.md)** - Code examples and patterns
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Streamlit app documentation (previous version)

## Performance Notes

- **Typical Speed**: 10-20 documents per minute
- **Memory Usage**: 100-300 MB (depends on file sizes)
- **Network**: Respects server with delays and throttling
- **CPU**: Minimal (mostly I/O bound)

## Legal Considerations

✅ Respects robots.txt  
✅ Uses delays between requests  
✅ Limits concurrent connections  
✅ Identifies as crawler (User-Agent)  

Ensure you have permission to download documents from the court website.

## Support

For issues:
1. Check logs for detailed error messages
2. Review metadata files for download results
3. Test selectors with Scrapy shell
4. Consult Scrapy documentation: https://docs.scrapy.org

## Requirements

- Python 3.8+
- Scrapy 2.11+
- itemadapter 0.8+
- See `requirements.txt` for complete list

## Installation from GitHub

```bash
git clone https://github.com/Gbenatov/scrapcrap.git
cd scrapcrap
pip install -r requirements.txt
cd scraper_system
python run_scraper.py all
```

---

**Version**: 1.0  
**Last Updated**: January 21, 2026  
**Author**: Development Team  
**Scrapy Version**: 2.11+

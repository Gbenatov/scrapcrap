# Scrapy-Based Court Document Downloader Guide

## Overview

This system provides a complete Scrapy-based solution for downloading documents from the Israeli Court's class action register (פנקס תובענות ייצוגיות). It uses Scrapy's FilesPipeline to handle document downloads while following links to locate documents on multiple pages.

## Architecture

### Components

1. **CourtDocumentSpider** (`court_document_scraper.py`)
   - Main spider for scraping case pages
   - Extracts case information and document URLs
   - Uses FilesPipeline for downloading
   - Follows links to access nested pages

2. **DocumentLinkFollowerSpider** (`court_document_scraper.py`)
   - Alternative spider focused on link traversal
   - Useful when documents are behind multiple click layers
   - Has depth limit to prevent infinite loops
   - Respectful crawling with delays

3. **CourtDocumentPipeline** (`pipelines.py`)
   - Custom pipeline extending FilesPipeline
   - Organizes files by case number
   - Stores metadata (JSONL format)
   - Tracks download success/failure

4. **DocumentMetadataExporter** (`pipelines.py`)
   - Reads and analyzes download metadata
   - Generates JSON and CSV reports
   - Provides download statistics

## How It Works

### Flow Diagram

```
Start URL (Class Actions Index)
    ↓
Parse case links
    ↓
For each case:
  - Extract case details (number, title, status)
  - Find document URLs
  - Send to FilesPipeline
    ↓
FilesPipeline:
  - Downloads each document
  - Organizes by case number
  - Stores metadata
    ↓
Post-processing:
  - Generate reports (JSON, CSV)
  - Display statistics
```

### Key Features

1. **Link Following**: Automatically follows links to find documents on multiple pages
2. **Metadata Storage**: Saves case information alongside documents
3. **Error Handling**: Gracefully handles failed downloads and network errors
4. **Respectful Crawling**: Respects robots.txt, uses delays, limits concurrency
5. **Progress Tracking**: Stores metadata about each download attempt
6. **Report Generation**: Creates summaries of download results

## Installation & Setup

### 1. Install Dependencies

```bash
pip install scrapy itemadapter
```

### 2. Project Structure

Ensure your project has:
```
scraper_system/
├── court_document_scraper.py    # Spider definitions
├── pipelines.py                 # Custom pipelines
├── settings.py                  # Scrapy settings
├── run_scraper.py              # CLI runner
└── __init__.py
```

### 3. Configure Storage Location

Edit `settings.py` to set where documents should be saved:
```python
FILES_STORE = '/path/to/downloads/court_documents'
```

## Usage

### Basic Usage

#### 1. Run Main Spider

```bash
cd scraper_system
python run_scraper.py scrape
```

This will:
- Start from the court.gov.il class actions page
- Extract case links
- Download all associated documents
- Store metadata

#### 2. Run Link Follower Spider

```bash
python run_scraper.py follow
```

This spider is more thorough, following additional links to find hidden documents.

#### 3. Generate Reports

```bash
python run_scraper.py report
```

Generates:
- `downloads/report.json` - Detailed JSON report
- `downloads/documents.csv` - CSV spreadsheet

#### 4. Run Full Pipeline

```bash
python run_scraper.py all
```

Combines all steps: crawling, downloading, and reporting.

### Advanced Usage

#### Run with Custom Start URL

```bash
python run_scraper.py scrape --start-url "https://example.com/cases"
```

#### Run Scrapy Command Line Directly

```bash
# Run spider with custom settings
scrapy crawl court_documents -L INFO

# Run follower spider
scrapy crawl court_documents_follower -L INFO

# Export results to JSON
scrapy crawl court_documents -o results.json
```

## Output Structure

### Downloaded Files

```
downloads/
├── court_documents/
│   ├── case_12345/
│   │   ├── decision.pdf
│   │   ├── summons.pdf
│   │   └── judgment.docx
│   ├── case_12346/
│   │   ├── agreement.pdf
│   │   └── notice.doc
│   └── metadata.jsonl         # Case metadata (JSONL format)
├── report.json                # Summary report
└── documents.csv              # Spreadsheet of all cases
```

### Metadata Structure (JSONL)

Each line in `metadata.jsonl`:
```json
{
  "timestamp": "2026-01-21T10:30:45.123456",
  "case_number": "01-12345",
  "case_title": "תובענה ייצוגית נגד חברה X",
  "case_url": "https://www.court.gov.il/...",
  "case_status": "Active",
  "court_name": "District Court of Tel Aviv",
  "judge_name": "Judge Name",
  "parties": "Plaintiff vs Defendant",
  "requested_files": 5,
  "downloaded_files": 4,
  "failed_downloads": 1,
  "file_paths": ["case_12345/file1.pdf", "case_12345/file2.pdf"],
  "failed_urls": ["https://example.com/missing.pdf"]
}
```

### Report Structure

```json
{
  "generated": "2026-01-21T10:45:30.123456",
  "total_cases": 45,
  "total_files_requested": 234,
  "total_files_downloaded": 218,
  "total_failures": 16,
  "success_rate": 93.2,
  "cases": [
    { ... metadata records ... }
  ]
}
```

## Configuration

### Scrapy Settings (in `settings.py`)

Key settings you may want to adjust:

```python
# Crawling speed
CONCURRENT_REQUESTS = 8        # Number of parallel requests
DOWNLOAD_DELAY = 2             # Seconds between requests
DOWNLOAD_TIMEOUT = 30          # Seconds to wait for response

# Robot compliance
ROBOTSTXT_OBEY = True          # Respect robots.txt
AUTOTHROTTLE_ENABLED = True    # Auto-adjust speed based on server response

# Storage
FILES_STORE = 'downloads/court_documents'
FILES_EXPIRES = 90             # Days to keep cached files

# Memory
MEMUSAGE_LIMIT_MB = 256        # Maximum memory to use
MEMUSAGE_CHECK_INTERVAL_SECONDS = 60

# Logging
LOG_LEVEL = 'INFO'             # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Spider-Specific Settings

Both spiders have custom settings defined in their classes:

```python
custom_settings = {
    'ITEM_PIPELINES': {...},
    'FILES_STORE': '...',
    'DEPTH_LIMIT': 3,
}
```

## Examples

### Example 1: Scrape and Download All Court Documents

```bash
python run_scraper.py all
```

Output:
```
2026-01-21 10:30:00 [scrapy.core.engine] INFO: Starting scraper
2026-01-21 10:30:05 [court_document_scraper] INFO: Parsing main page
2026-01-21 10:30:10 [court_document_scraper] INFO: Found 45 case links
...
==================================================
DOWNLOAD REPORT
==================================================
Total cases: 45
Files requested: 234
Files downloaded: 218
Failed downloads: 16
Success rate: 93.2%
==================================================
```

### Example 2: Process Specific Case

Modify spider to start from specific case:
```python
start_urls = [
    'https://www.court.gov.il/he/Units/TabuPublic/Pages/CaseDetails.aspx?CaseID=123456'
]
```

### Example 3: Analyze Results with CSV

After running, open `downloads/documents.csv` in Excel/Sheets:
- Sort by `downloaded_files` to find cases with most documents
- Filter by `case_status` to focus on active cases
- Check `success_rate` to identify problem cases

## Troubleshooting

### Issue: "No case links found"

**Cause**: Website structure may have changed
**Solution**:
1. Check website manually in browser
2. Update CSS selectors in spider's `parse()` method
3. Use Scrapy shell to debug selectors:
   ```bash
   scrapy shell "https://www.court.gov.il/..."
   response.css('a::attr(href)').getall()
   ```

### Issue: Downloads are too slow

**Solution**: Increase concurrent requests (carefully)
```python
CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 1
```

### Issue: Memory usage too high

**Solution**: Lower memory limit or reduce concurrent requests
```python
CONCURRENT_REQUESTS = 4
MEMUSAGE_LIMIT_MB = 128
```

### Issue: Many failed downloads

**Cause**: Files may have moved or permission issues
**Solution**:
1. Check `failed_urls` in metadata.jsonl
2. Verify URLs manually in browser
3. Check server error codes in logs

## Advanced: Custom Spider Development

### Create Your Own Spider

```python
from scrapy import Spider, Request
from court_document_scraper import CourtDocumentItem

class CustomCourtSpider(Spider):
    name = 'custom_court'
    start_urls = ['https://www.court.gov.il/...']
    
    custom_settings = {
        'FILES_STORE': 'downloads/custom',
    }
    
    def parse(self, response):
        # Your custom logic
        item = CourtDocumentItem()
        item['case_number'] = response.css('...').get()
        item['file_urls'] = response.css('a[href$=".pdf"]::attr(href)').getall()
        yield item
```

### Debug with Scrapy Shell

```bash
scrapy shell "https://www.court.gov.il/..."

# Try selectors interactively
response.css('h1::text').get()
response.xpath('//a/@href').getall()
response.css('a[href*="case"]::attr(href)').getall()
```

## Performance Tips

1. **Use Response Caching**: Enabled by default, speeds up re-runs
2. **Limit Depth**: Set `DEPTH_LIMIT` to avoid infinite loops
3. **Batch Downloads**: Use `CONCURRENT_REQUESTS` wisely (8-16 optimal)
4. **Add Delays**: Respect server with `DOWNLOAD_DELAY`
5. **Monitor Memory**: Use `MEMUSAGE_LIMIT_MB` to prevent crashes

## Legal Considerations

- Always check `robots.txt` (enabled by default)
- Respect `Retry-After` headers
- Don't overload the server with too many concurrent requests
- Ensure you have permission to download and use the documents
- Follow local laws regarding web scraping

## Support & Issues

For issues or questions:

1. Check Scrapy documentation: https://docs.scrapy.org
2. Review spider logs for errors
3. Test selectors with Scrapy shell
4. Check metadata files for download results

---

**Last Updated**: January 21, 2026
**Version**: 1.0
**Scrapy Version**: 2.11+

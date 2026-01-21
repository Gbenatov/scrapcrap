# Scrapy FilesPipeline Examples

This document provides code examples for the Israeli Court Document Scraper using Scrapy's FilesPipeline.

## Example 1: Basic Spider with File Downloads

```python
import scrapy
from scrapy.pipelines.files import FilesPipeline

class DocumentItem(scrapy.Item):
    case_number = scrapy.Field()
    file_urls = scrapy.Field()    # URLs to download
    files = scrapy.Field()         # Results from FilesPipeline

class CaseSpider(scrapy.Spider):
    name = 'basic_case_spider'
    start_urls = ['https://www.court.gov.il/...']
    
    custom_settings = {
        'ITEM_PIPELINES': {
            'scrapy.pipelines.files.FilesPipeline': 1,
        },
        'FILES_STORE': 'downloads/',
        'FILES_URLS_FIELD': 'file_urls',
        'FILES_RESULT_FIELD': 'files',
    }
    
    def parse(self, response):
        item = DocumentItem()
        item['case_number'] = response.css('.case-num::text').get()
        
        # Extract all document links
        item['file_urls'] = response.css('a[href$=".pdf"], a[href$=".doc"]::attr(href)').getall()
        
        yield item  # FilesPipeline automatically downloads files
```

## Example 2: Following Links to Find Documents

```python
import scrapy
from urllib.parse import urljoin

class LinkFollowerSpider(scrapy.Spider):
    name = 'link_follower'
    start_urls = ['https://www.court.gov.il/he/Units/TabuPublic/']
    
    def parse(self, response):
        """Extract and follow case links"""
        # Find all case detail links
        for case_link in response.css('a[href*="case"]::attr(href)').getall():
            absolute_url = urljoin(response.url, case_link)
            yield scrapy.Request(
                absolute_url,
                callback=self.parse_case,
                meta={'source': response.url}
            )
    
    def parse_case(self, response):
        """Extract documents from case page"""
        # Find document URLs
        documents = response.css('a[href$=".pdf"], a[href$=".doc"]::attr(href)').getall()
        
        if documents:
            yield {
                'case_url': response.url,
                'documents': [urljoin(response.url, doc) for doc in documents],
                'document_count': len(documents)
            }
        
        # Follow related links (e.g., decisions, appeals)
        for related_link in response.css('a[href*="decision"], a[href*="appeal"]::attr(href)').getall():
            absolute_url = urljoin(response.url, related_link)
            # Limit depth to avoid infinite loops
            if response.meta.get('depth', 0) < 2:
                yield scrapy.Request(
                    absolute_url,
                    callback=self.parse_case,
                    meta={'depth': response.meta.get('depth', 0) + 1}
                )
```

## Example 3: Custom Pipeline with Metadata Storage

```python
from scrapy.pipelines.files import FilesPipeline
from itemadapter import ItemAdapter
from datetime import datetime
import json
import os

class MetadataStoragePipeline(FilesPipeline):
    """Custom pipeline that organizes files and stores metadata"""
    
    def open_spider(self, spider):
        super().open_spider(spider)
        self.metadata_file = os.path.join(
            self.store_uri, 
            'download_metadata.jsonl'
        )
    
    def file_path(self, request, response=None, info=None, *, item=None):
        """Organize files by case number"""
        if item:
            adapter = ItemAdapter(item)
            case_number = adapter.get('case_number', 'unknown')
            # Sanitize case number
            safe_case = ''.join(c if c.isalnum() else '_' for c in case_number)
            filename = request.url.split('/')[-1] or 'document'
            return f"{safe_case}/{filename}"
        
        return super().file_path(request, response, info, item=item)
    
    def item_completed(self, results, item, info):
        """Save metadata about downloads"""
        adapter = ItemAdapter(item)
        
        file_paths = []
        for success, file_info in results:
            if success:
                file_paths.append(file_info['path'])
        
        # Create metadata record
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'case_number': adapter.get('case_number'),
            'case_url': adapter.get('case_url'),
            'requested_files': len(adapter.get('file_urls', [])),
            'downloaded_files': len(file_paths),
            'file_paths': file_paths,
        }
        
        # Append to JSONL file
        with open(self.metadata_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(metadata, ensure_ascii=False) + '\n')
        
        return item
```

## Example 4: Settings Configuration

```python
# settings.py

BOT_NAME = 'court_document_scraper'

# FilesPipeline configuration
ITEM_PIPELINES = {
    'scrapy.pipelines.files.FilesPipeline': 1,
    'myproject.pipelines.MetadataStoragePipeline': 2,
}

# Storage settings
FILES_STORE = 'downloads/documents'
FILES_URLS_FIELD = 'file_urls'
FILES_RESULT_FIELD = 'files'
FILES_EXPIRES = 90  # Keep downloaded files for 90 days

# Request settings
CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 2  # Respectful crawling
DOWNLOAD_TIMEOUT = 30

# Robot compliance
ROBOTSTXT_OBEY = True
USER_AGENT = 'Mozilla/5.0 (compatible; CrawlerBot/1.0)'

# AutoThrottle to adjust speed dynamically
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 10

# HTTP caching
HTTPCACHE_ENABLED = True
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
```

## Example 5: Report Generation

```python
import json
import csv
from pathlib import Path
from datetime import datetime

class ReportGenerator:
    """Generate reports from downloaded data"""
    
    def __init__(self, metadata_file):
        self.metadata_file = metadata_file
        self.records = self._load_metadata()
    
    def _load_metadata(self):
        """Load JSONL metadata file"""
        records = []
        if Path(self.metadata_file).exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))
        return records
    
    def generate_json_report(self, output_file='report.json'):
        """Generate JSON report"""
        report = {
            'generated': datetime.now().isoformat(),
            'total_cases': len(self.records),
            'total_requested': sum(r.get('requested_files', 0) for r in self.records),
            'total_downloaded': sum(r.get('downloaded_files', 0) for r in self.records),
            'success_rate': None,
            'cases': self.records
        }
        
        if report['total_requested'] > 0:
            report['success_rate'] = (
                report['total_downloaded'] / report['total_requested'] * 100
            )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report
    
    def generate_csv_report(self, output_file='cases.csv'):
        """Generate CSV report"""
        if not self.records:
            return
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'timestamp', 'case_number', 'case_url',
                'requested_files', 'downloaded_files'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for record in self.records:
                writer.writerow({k: record.get(k) for k in fieldnames})
    
    def print_summary(self):
        """Print summary statistics"""
        print("\n" + "="*50)
        print("DOWNLOAD SUMMARY")
        print("="*50)
        print(f"Total cases processed: {len(self.records)}")
        
        if self.records:
            total_req = sum(r.get('requested_files', 0) for r in self.records)
            total_dl = sum(r.get('downloaded_files', 0) for r in self.records)
            
            print(f"Total files requested: {total_req}")
            print(f"Total files downloaded: {total_dl}")
            
            if total_req > 0:
                success_rate = (total_dl / total_req) * 100
                print(f"Success rate: {success_rate:.1f}%")
        
        print("="*50 + "\n")

# Usage
if __name__ == '__main__':
    generator = ReportGenerator('downloads/download_metadata.jsonl')
    generator.generate_json_report('reports/summary.json')
    generator.generate_csv_report('reports/cases.csv')
    generator.print_summary()
```

## Example 6: Running the Spider

```bash
# Install Scrapy
pip install scrapy

# Run spider
cd scraper_system
scrapy crawl court_documents -L INFO

# Export to JSON
scrapy crawl court_documents -o results.json

# Run with custom settings
scrapy crawl court_documents -s FILES_STORE=my_downloads/

# Debug selectors
scrapy shell "https://www.court.gov.il/..."
# Then try:
# response.css('a::attr(href)').getall()
# response.css('a[href$=".pdf"]::attr(href)').getall()
```

## Example 7: Error Handling

```python
import scrapy
from scrapy.exceptions import DropItem

class RobustCaseSpider(scrapy.Spider):
    name = 'robust_scraper'
    start_urls = ['https://www.court.gov.il/...']
    
    def parse(self, response):
        """Parse with comprehensive error handling"""
        try:
            case_item = scrapy.Item()
            
            # Safely extract data with fallbacks
            case_item['case_number'] = (
                response.css('.case-num::text').get() or 'UNKNOWN'
            )
            case_item['case_title'] = (
                response.css('h1::text').get() or 'No title'
            )
            
            # Extract document URLs
            doc_urls = response.css('a[href$=".pdf"]::attr(href)').getall()
            if not doc_urls:
                self.logger.warning(f'No documents found for {case_item["case_number"]}')
                raise DropItem("No documents found")
            
            case_item['file_urls'] = doc_urls
            yield case_item
            
        except Exception as e:
            self.logger.error(f'Error parsing {response.url}: {e}')
    
    def errback_handler(self, failure):
        """Handle request failures"""
        self.logger.error(f'Request failed: {failure.request.url}')
        self.logger.error(f'Error: {failure.value}')
```

## Key Concepts

### FilesPipeline Features

- **Automatic Download**: Files are downloaded automatically when you yield items with `file_urls`
- **Organization**: Customize where files are stored with `file_path()` method
- **Caching**: Files already downloaded are not re-downloaded
- **Metadata**: Results are returned in the `files` field

### Best Practices

1. **Organize by Case**: Use `file_path()` to organize downloaded files
2. **Store Metadata**: Keep records of what was downloaded and when
3. **Handle Errors**: Use try-except blocks and custom error handlers
4. **Respect Servers**: Use `DOWNLOAD_DELAY` and `AUTOTHROTTLE`
5. **Cache Results**: Enable HTTP caching to avoid re-downloading
6. **Monitor Progress**: Log important events and statistics

### Common Pitfalls

- **Too Many Concurrent Requests**: Can overload the server (use CONCURRENT_REQUESTS=8)
- **No Delays**: Can get blocked (set DOWNLOAD_DELAY=2)
- **Missing Metadata**: Always save information about downloads for records
- **Infinite Loops**: Use depth limits when following links
- **Memory Issues**: Monitor with MEMUSAGE_LIMIT_MB

---

**For more details, see**: [SCRAPY_GUIDE.md](SCRAPY_GUIDE.md)

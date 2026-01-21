# Quick Reference Guide - Scrapy FilesPipeline Document Downloader

## 🚀 Quick Start (60 seconds)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Run
cd scraper_system
python run_scraper.py all

# 3. Check results
ls downloads/court_documents/
cat downloads/report.json
```

## 📋 Command Reference

| Command | Purpose | Output |
|---------|---------|--------|
| `python run_scraper.py all` | Full pipeline | Downloads + Reports |
| `python run_scraper.py scrape` | Just spider | Downloaded files |
| `python run_scraper.py follow` | Link follower | Downloaded files |
| `python run_scraper.py report` | Just reports | JSON + CSV |
| `scrapy crawl court_documents` | Direct Scrapy | Downloaded files |

## 📁 Output Structure

```
downloads/
├── court_documents/           # Downloaded files
│   ├── case_12345/           # Organized by case
│   │   ├── doc1.pdf          # Downloaded document
│   │   ├── doc2.pdf
│   │   └── doc3.docx
│   ├── case_12346/
│   │   └── agreement.pdf
│   └── metadata.jsonl        # Case information (1 JSON per line)
├── report.json               # Summary statistics
└── documents.csv             # Spreadsheet export
```

## 🔍 File Naming

Files are automatically organized:
```
case_NUMBER/filename.ext

Example:
case_01234/decision.pdf
case_01234/summons.pdf
case_01235/agreement.pdf
```

## 📊 Report Contents

### metadata.jsonl (One entry per case)
```json
{
  "timestamp": "2026-01-21T10:30:00",
  "case_number": "01-12345",
  "case_title": "תובענה ייצוגית",
  "requested_files": 5,
  "downloaded_files": 4,
  "failed_downloads": 1,
  "file_paths": ["case_12345/doc1.pdf"],
  "failed_urls": ["https://...missing.pdf"]
}
```

### report.json (Summary)
```json
{
  "total_cases": 45,
  "total_files_requested": 234,
  "total_files_downloaded": 218,
  "success_rate": 93.2
}
```

### documents.csv (Spreadsheet)
```
timestamp,case_number,requested_files,downloaded_files
2026-01-21T10:30:00,01-12345,5,4
2026-01-21T10:35:00,01-12346,3,3
```

## ⚙️ Configuration Presets

### Fast (Less Respectful)
```python
CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 1
```

### Balanced (Recommended)
```python
CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 2
```

### Slow (Very Respectful)
```python
CONCURRENT_REQUESTS = 4
DOWNLOAD_DELAY = 5
```

Edit in `scraper_system/settings.py`

## 🐛 Troubleshooting Quick Links

| Problem | Solution |
|---------|----------|
| No files found | Check website, update selectors in spider |
| Many failures | Verify URLs in `failed_urls` section |
| Too slow | Increase `CONCURRENT_REQUESTS` |
| High memory | Decrease `CONCURRENT_REQUESTS` |
| Getting blocked | Increase `DOWNLOAD_DELAY` |

## 🔧 Troubleshooting Steps

### Step 1: Debug Selectors
```bash
scrapy shell "https://www.court.gov.il/..."
response.css('a[href$=".pdf"]::attr(href)').getall()
```

### Step 2: Check Logs
```bash
scrapy crawl court_documents -L DEBUG
```

### Step 3: Inspect Metadata
```bash
# See what failed
grep "failed_downloads" downloads/court_documents/metadata.jsonl

# Count successes
wc -l downloads/court_documents/metadata.jsonl
```

## 📦 Files Created

### Code Files
```
scraper_system/
├── court_document_scraper.py   # Spiders (350 lines)
├── pipelines.py                # Pipeline (200 lines)
├── settings.py                 # Config (70 lines)
└── run_scraper.py             # CLI runner (150 lines)
```

### Documentation
```
├── SCRAPY_README.md            # Overview
├── SCRAPY_GUIDE.md             # Detailed guide (600 lines)
├── SCRAPY_EXAMPLES.md          # 7 code examples
├── IMPLEMENTATION_SUMMARY.md   # What was built
└── QUICK_REFERENCE.md          # This file!
```

## 🎯 Typical Workflow

```
1. Review Website Manually
   └─> Understand page structure

2. Update Selectors (if needed)
   └─> Edit spider CSS selectors

3. Run Spider
   └─> python run_scraper.py scrape

4. Check Results
   └─> ls downloads/court_documents/

5. Review Failures
   └─> Check metadata.jsonl for failed_urls

6. Generate Reports
   └─> python run_scraper.py report

7. Analyze
   └─> Open documents.csv in Excel
```

## 🚦 Performance Expectations

| Metric | Value |
|--------|-------|
| Download Speed | 10-20 docs/min |
| Memory Usage | 100-300 MB |
| Concurrent Requests | 8 (default) |
| Retry Attempts | 3 |
| Timeout | 30 seconds |

## 🔒 Safety Features

✅ Respects robots.txt  
✅ Uses delays (2 sec default)  
✅ Limits concurrency (8 default)  
✅ Auto-throttles  
✅ Retries failed requests  
✅ Logs all activity  

## 💾 Memory Management

```python
# Prevent memory overload
MEMUSAGE_LIMIT_MB = 256        # Stop if exceeds this
MEMUSAGE_CHECK_INTERVAL_SECONDS = 60
```

If you see memory warnings:
1. Decrease `CONCURRENT_REQUESTS` to 4
2. Reduce `MEMUSAGE_LIMIT_MB` to 128
3. Run reports separately

## 📋 Spider Selector Reference

Update in `court_document_scraper.py`:

```python
# Find case links
response.css('a[href*="case"]::attr(href)').getall()

# Find PDF links
response.css('a[href$=".pdf"]::attr(href)').getall()

# Find all doc links
response.css('a[href$=".doc"], a[href$=".docx"]::attr(href)').getall()

# By ID
response.css('#case-link::attr(href)').getall()

# By class
response.css('a.case-link::attr(href)').getall()

# By attribute
response.css('a[data-type="case"]::attr(href)').getall()
```

## 🎨 Customization Examples

### Download Only PDFs
```python
def _extract_document_urls(self, response):
    # Only PDF documents
    return response.css('a[href$=".pdf"]::attr(href)').getall()
```

### Store by Date
```python
def file_path(self, request, response=None, info=None, *, item=None):
    date = datetime.now().strftime('%Y-%m-%d')
    case = ItemAdapter(item).get('case_number')
    return f'{date}/{case}/{request.url.split("/")[-1]}'
```

### Custom Filename
```python
def file_path(self, request, response=None, info=None, *, item=None):
    case = ItemAdapter(item).get('case_number')
    doc_type = request.url.split('type=')[-1] if 'type=' in request.url else 'doc'
    return f'{case}/{doc_type}.pdf'
```

## 📞 Getting Help

### Check Documentation
1. [SCRAPY_README.md](SCRAPY_README.md) - Overview
2. [SCRAPY_GUIDE.md](SCRAPY_GUIDE.md) - Detailed guide
3. [SCRAPY_EXAMPLES.md](SCRAPY_EXAMPLES.md) - Code examples

### Debug Steps
```bash
# 1. Enable debug logging
scrapy crawl court_documents -L DEBUG

# 2. Test selectors interactively
scrapy shell "https://www.court.gov.il/..."

# 3. Check metadata files
cat downloads/court_documents/metadata.jsonl | head -1 | python -m json.tool
```

## 🔗 Useful Links

- Scrapy Docs: https://docs.scrapy.org
- FilesPipeline: https://docs.scrapy.org/en/latest/topics/media-pipeline.html
- Selectors: https://docs.scrapy.org/en/latest/topics/selectors.html
- GitHub Repo: https://github.com/Gbenatov/scrapcrap

## 📝 Common Tasks

### View all downloaded cases
```bash
ls -d downloads/court_documents/case_*/
```

### Count downloaded files
```bash
find downloads/court_documents -type f ! -name "metadata.jsonl" ! -name ".gitkeep" | wc -l
```

### See failed downloads
```bash
cat downloads/court_documents/metadata.jsonl | grep -o '"failed_urls":\[[^]]*\]' | head -3
```

### Generate fresh report
```bash
python scraper_system/run_scraper.py report
```

### Check memory usage
```bash
ps aux | grep python
```

## ⚡ Pro Tips

1. **First Run**: Start with 1-2 cases to test selectors
2. **Enable Cache**: HTTP caching speeds up re-runs
3. **Monitor Logs**: Watch for patterns in failures
4. **Backup Metadata**: Keep metadata.jsonl for auditing
5. **Use CSV Reports**: Easy to analyze in Excel

## ✅ Verification Checklist

After running, verify:

- [ ] Downloads folder created
- [ ] Files organized by case
- [ ] metadata.jsonl has entries
- [ ] report.json generated
- [ ] documents.csv created
- [ ] No permission errors in logs
- [ ] Success rate > 90%

## 🎯 Next Steps

1. **Customize**: Update spider selectors for your website
2. **Test**: Run with 1-2 cases first
3. **Monitor**: Watch logs for issues
4. **Scale**: Increase CONCURRENT_REQUESTS once stable
5. **Automate**: Set up cron job for regular runs

---

**Version**: 1.0 | **Updated**: Jan 21, 2026 | **Status**: ✅ Ready to Use

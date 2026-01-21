# Scrapy settings for court document scraper

BOT_NAME = 'court_document_scraper'

SPIDER_MODULES = ['scraper_system.court_document_scraper']
NEWSPIDER_MODULE = 'scraper_system.court_document_scraper'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests made by Scrapy (default: 16)
CONCURRENT_REQUESTS = 8

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 2

# The download timeout used by the default HttpCacheMiddleware.
DOWNLOAD_TIMEOUT = 30

# HTTP caching enabled
HTTPCACHE_ENABLED = True
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
HTTPCACHE_DIR = 'downloads/.httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [400, 403, 404, 500, 503]

# Disable cookies (set to False if you need to maintain sessions)
COOKIES_ENABLED = False

# Disable Telnet Console (beware of security implications)
TELNETCONSOLE_ENABLED = False

# Set levels for loggers
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'

# Files Pipeline settings
FILES_STORE = 'downloads/court_documents'
FILES_URLS_FIELD = 'file_urls'
FILES_RESULT_FIELD = 'files'
FILES_EXPIRES = 90
FILES_MIN_SIZE = 0  # Download all files regardless of size

# Retry settings
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408]

# Item pipelines
ITEM_PIPELINES = {
    'scrapy.pipelines.files.FilesPipeline': 1,
    'scraper_system.pipelines.CourtDocumentPipeline': 2,
}

# Middleware configuration
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': 543,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 580,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 590,
}

# User Agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Depth limit
DEPTH_LIMIT = 2

# Adjust settings such as AUTOTHROTTLE settings
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 4.0

# Memory usage optimization
MEMDEBUG_ENABLED = False
MEMUSAGE_ENABLED = True
MEMUSAGE_LIMIT_MB = 256
MEMUSAGE_CHECK_INTERVAL_SECONDS = 60.0

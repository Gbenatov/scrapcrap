"""
Court Document Scraper
Downloads documents from Israeli court class action register (פנקס תובענות ייצוגיות)
Uses Scrapy's FilesPipeline to handle downloads and link following
"""

import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
import logging


class CourtDocumentItem(scrapy.Item):
    """Item for storing court case data and document URLs"""
    case_number = scrapy.Field()
    case_title = scrapy.Field()
    case_status = scrapy.Field()
    case_url = scrapy.Field()
    file_urls = scrapy.Field()  # URLs of documents to download
    files = scrapy.Field()      # Results from FilesPipeline
    file_paths = scrapy.Field() # Paths of downloaded files
    court_name = scrapy.Field()
    judge_name = scrapy.Field()
    parties = scrapy.Field()


class CourtDocumentSpider(scrapy.Spider):
    """
    Spider for scraping documents from Israeli court class action register
    
    Starts from a case list page, extracts case links, then follows each link
    to extract document URLs, which are then downloaded by FilesPipeline
    """
    name = 'court_documents'
    allowed_domains = ['court.gov.il']
    start_urls = [
        'https://www.court.gov.il/he/Units/TabuPublic/Pages/CourtClassActionsIndex.aspx'
    ]
    
    custom_settings = {
        'ITEM_PIPELINES': {
            'scrapy.pipelines.files.FilesPipeline': 1,
            'scraper_system.pipelines.CourtDocumentPipeline': 2,
        },
        'FILES_STORE': 'downloads/court_documents',
        'FILES_URLS_FIELD': 'file_urls',
        'FILES_RESULT_FIELD': 'files',
        'FILES_EXPIRES': 90,
        'DOWNLOAD_TIMEOUT': 30,
    }
    
    logger = logging.getLogger(__name__)

    def parse(self, response):
        """
        Parse the main class actions index page
        Extract links to individual case pages
        """
        self.logger.info(f'Parsing main page: {response.url}')
        
        # Try to find links to case pages (adjust selector based on actual HTML structure)
        case_links = response.css('a[href*="/he/Units/TabuPublic/"]::attr(href)').getall()
        
        if not case_links:
            self.logger.warning('No case links found on main page. Trying alternative selectors...')
            case_links = response.css('a::attr(href)').getall()
        
        for link in case_links:
            # Filter for relevant links (cases, documents, etc.)
            if any(keyword in link.lower() for keyword in ['case', 'judgment', 'document', 'misgeret', 'taba']):
                absolute_url = urljoin(response.url, link)
                self.logger.info(f'Found case link: {absolute_url}')
                yield scrapy.Request(
                    absolute_url,
                    callback=self.parse_case_page,
                    dont_filter=True,
                    meta={'source_url': response.url}
                )

    def parse_case_page(self, response):
        """
        Parse individual case page
        Extract case details and document URLs
        """
        self.logger.info(f'Parsing case page: {response.url}')
        
        item = CourtDocumentItem()
        
        # Extract case information
        item['case_url'] = response.url
        item['case_number'] = response.css('span.case-number::text').get() or 'Unknown'
        item['case_title'] = response.css('span.case-title::text').get() or response.css('h1::text').get() or 'Unknown'
        item['case_status'] = response.css('span.case-status::text').get() or 'Unknown'
        item['court_name'] = response.css('span.court-name::text').get() or 'Court'
        item['judge_name'] = response.css('span.judge-name::text').get() or ''
        
        # Extract party information
        parties = response.css('div.party::text').getall()
        item['parties'] = ', '.join([p.strip() for p in parties if p.strip()]) or 'N/A'
        
        # Extract document URLs
        document_urls = self._extract_document_urls(response)
        item['file_urls'] = document_urls
        
        self.logger.info(f'Extracted {len(document_urls)} documents from {item["case_number"]}')
        
        # Only yield if documents were found
        if document_urls:
            yield item
        
        # Look for links to related pages (nested documents, decisions, etc.)
        related_links = response.css('a[href*="document"], a[href*="decision"], a[href*="judgment"]::attr(href)').getall()
        
        for link in related_links:
            absolute_url = urljoin(response.url, link)
            # Avoid infinite loops
            if absolute_url != response.url:
                yield scrapy.Request(
                    absolute_url,
                    callback=self.parse_case_page,
                    dont_filter=True,
                    meta={'source_url': response.url}
                )

    def _extract_document_urls(self, response):
        """
        Extract all downloadable document URLs from a case page
        Handles various document formats (PDF, DOC, DOCX, etc.)
        """
        document_urls = []
        
        # Look for direct document links
        doc_selectors = [
            'a[href$=".pdf"]::attr(href)',
            'a[href$=".doc"]::attr(href)',
            'a[href$=".docx"]::attr(href)',
            'a[href$=".xlsx"]::attr(href)',
            'a[href$=".xls"]::attr(href)',
            'a[href$=".rtf"]::attr(href)',
            'a[href*="download"]::attr(href)',
            'a[href*="document"]::attr(href)',
        ]
        
        for selector in doc_selectors:
            urls = response.css(selector).getall()
            for url in urls:
                if url not in document_urls:
                    absolute_url = urljoin(response.url, url)
                    # Validate URL before adding
                    if self._is_valid_document_url(absolute_url):
                        document_urls.append(absolute_url)
        
        return document_urls

    @staticmethod
    def _is_valid_document_url(url):
        """Validate if URL is likely a real document"""
        invalid_patterns = ['#', 'javascript:', 'mailto:', 'tel:']
        return not any(pattern in url.lower() for pattern in invalid_patterns)


class DocumentLinkFollowerSpider(scrapy.Spider):
    """
    Alternative spider that focuses on following links to find documents
    Useful when document URLs are behind links/buttons
    """
    name = 'court_documents_follower'
    allowed_domains = ['court.gov.il']
    start_urls = [
        'https://www.court.gov.il/he/Units/TabuPublic/Pages/CourtClassActionsIndex.aspx'
    ]
    
    custom_settings = {
        'DEPTH_LIMIT': 3,  # Limit recursion depth
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOAD_DELAY': 2,  # Be respectful to the server
    }
    
    logger = logging.getLogger(__name__)

    def parse(self, response):
        """Extract case links and follow them"""
        # Find all links that might lead to cases
        for link in response.css('a::attr(href)').getall():
            if self._is_case_link(link):
                absolute_url = urljoin(response.url, link)
                yield scrapy.Request(
                    absolute_url,
                    callback=self.parse_case,
                    errback=self.errback_handler,
                    dont_filter=True,
                    meta={'depth': 0}
                )

    def parse_case(self, response):
        """Parse case page and extract documents"""
        current_depth = response.meta.get('depth', 0)
        
        self.logger.info(f'Parsing at depth {current_depth}: {response.url}')
        
        # Extract and yield document URLs
        documents = self._find_documents(response)
        if documents:
            yield {
                'case_url': response.url,
                'documents': documents,
                'status': 'documents_found'
            }
        
        # Follow deeper links only if within depth limit
        if current_depth < 2:
            for link in response.css('a::attr(href)').getall():
                if self._should_follow_link(link):
                    absolute_url = urljoin(response.url, link)
                    # Avoid revisiting same URL
                    if absolute_url != response.url:
                        yield scrapy.Request(
                            absolute_url,
                            callback=self.parse_case,
                            errback=self.errback_handler,
                            dont_filter=True,
                            meta={'depth': current_depth + 1}
                        )

    @staticmethod
    def _is_case_link(link):
        """Determine if link likely points to a case"""
        case_keywords = [
            'case', 'misgeret', 'taba', 'judgment', 'decision',
            'tabu', 'class', 'action', 'number', 'case_id'
        ]
        return any(keyword in link.lower() for keyword in case_keywords)

    @staticmethod
    def _should_follow_link(link):
        """Determine if we should follow this link"""
        invalid_patterns = [
            'javascript:', 'mailto:', 'tel:', '#', '.pdf', '.doc',
            'logout', 'home', 'help', 'about'
        ]
        return not any(pattern in link.lower() for pattern in invalid_patterns)

    @staticmethod
    def _find_documents(response):
        """Find all document links in the response"""
        documents = []
        doc_extensions = ['.pdf', '.doc', '.docx', '.xlsx', '.xls', '.rtf']
        
        for link in response.css('a::attr(href)').getall():
            if any(link.lower().endswith(ext) for ext in doc_extensions):
                documents.append(urljoin(response.url, link))
        
        return documents

    def errback_handler(self, failure):
        """Handle request errors gracefully"""
        self.logger.error(f'Request failed: {failure.request.url}')
        self.logger.error(f'Error: {failure.value}')

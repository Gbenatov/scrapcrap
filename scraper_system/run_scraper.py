#!/usr/bin/env python
"""
Runner script for Scrapy court document scraper
Provides easy CLI interface to run spiders and generate reports
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add project to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.dirname(project_root))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from court_document_scraper import CourtDocumentSpider, DocumentLinkFollowerSpider
from pipelines import DocumentMetadataExporter


def run_spider(spider_class, spider_name, *args, **kwargs):
    """Run a Scrapy spider"""
    logging.info(f'Starting spider: {spider_name}')
    
    # Create process with custom settings
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOAD_DELAY': 2,
        'DOWNLOAD_TIMEOUT': 30,
        'FILES_STORE': 'downloads/court_documents',
        'ITEM_PIPELINES': {
            'scrapy.pipelines.files.FilesPipeline': 1,
            'scraper_system.pipelines.CourtDocumentPipeline': 2,
        },
        'LOG_LEVEL': 'INFO',
    })
    
    process.crawl(spider_class)
    process.start()
    
    logging.info(f'Spider {spider_name} completed')


def generate_report():
    """Generate report from downloaded metadata"""
    metadata_file = 'downloads/court_documents/metadata.jsonl'
    
    if not os.path.exists(metadata_file):
        logging.error(f'Metadata file not found: {metadata_file}')
        return
    
    exporter = DocumentMetadataExporter(metadata_file)
    
    # Generate both JSON and CSV reports
    logging.info('Generating reports...')
    report = exporter.generate_report('downloads/report.json')
    exporter.export_csv('downloads/documents.csv')
    
    if report:
        print('\n' + '='*50)
        print('DOWNLOAD REPORT')
        print('='*50)
        print(f"Total cases: {report['total_cases']}")
        print(f"Files requested: {report['total_files_requested']}")
        print(f"Files downloaded: {report['total_files_downloaded']}")
        print(f"Failed downloads: {report['total_failures']}")
        if report['success_rate'] is not None:
            print(f"Success rate: {report['success_rate']:.1f}%")
        print('='*50 + '\n')


def main():
    """Main entry point"""
    configure_logging({'LOG_LEVEL': 'INFO'})
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
    
    parser = argparse.ArgumentParser(
        description='Israeli Court Document Scraper'
    )
    parser.add_argument(
        'command',
        choices=['scrape', 'follow', 'report', 'all'],
        help='Command to run'
    )
    parser.add_argument(
        '--start-url',
        help='Starting URL to scrape',
        default='https://www.court.gov.il/he/Units/TabuPublic/Pages/CourtClassActionsIndex.aspx'
    )
    
    args = parser.parse_args()
    
    # Create downloads directory
    os.makedirs('downloads/court_documents', exist_ok=True)
    
    if args.command == 'scrape':
        run_spider(CourtDocumentSpider, 'CourtDocumentSpider')
    
    elif args.command == 'follow':
        run_spider(DocumentLinkFollowerSpider, 'DocumentLinkFollowerSpider')
    
    elif args.command == 'report':
        generate_report()
    
    elif args.command == 'all':
        logging.info('Running full pipeline...')
        run_spider(DocumentLinkFollowerSpider, 'DocumentLinkFollowerSpider')
        generate_report()


if __name__ == '__main__':
    main()

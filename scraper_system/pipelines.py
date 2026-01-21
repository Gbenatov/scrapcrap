"""
Custom Scrapy Pipelines for Court Document Scraping
Handles file download integration and document metadata storage
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from scrapy.pipelines.files import FilesPipeline
from scrapy.http import Request
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class CourtDocumentPipeline(FilesPipeline):
    """
    Custom pipeline extending FilesPipeline
    Stores document metadata alongside downloaded files
    """
    
    def __init__(self, store_uri, download_timeout=None, download_slot=None,
                 auto_mkdir=True, crawl_modules=None):
        super().__init__(store_uri, download_timeout, download_slot, auto_mkdir)
        self.logger = logging.getLogger(self.__class__.__name__)

    def open_spider(self, spider):
        """Initialize metadata storage when spider opens"""
        super().open_spider(spider)
        self.metadata_file = os.path.join(
            self.store_uri if isinstance(self.store_uri, str) else str(self.store_uri),
            'metadata.jsonl'
        )
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.metadata_file), exist_ok=True)
        self.logger.info(f'Metadata will be stored in: {self.metadata_file}')

    def file_path(self, request, response=None, info=None, *, item=None):
        """
        Customize file paths to organize by case number
        Structure: case_number/filename
        """
        if item:
            adapter = ItemAdapter(item)
            case_number = adapter.get('case_number', 'unknown')
            # Sanitize case number for use in filename
            case_number = ''.join(c if c.isalnum() else '_' for c in case_number)
        else:
            case_number = 'unknown'
        
        # Get original filename from URL
        filename = request.url.split('/')[-1]
        if not filename or filename.endswith('.'):
            filename = f'document_{int(datetime.now().timestamp())}'
        
        # Build organized path
        return f'{case_number}/{filename}'

    def get_media_requests(self, item, info):
        """Get file URLs from the item for download"""
        adapter = ItemAdapter(item)
        urls = adapter.get('file_urls', [])
        
        for url in urls:
            if isinstance(url, str) and url.strip():
                try:
                    yield Request(
                        url,
                        meta={'dont_redirect': False, 'dont_obey_robotstxt': False},
                        errback=self.file_download_error
                    )
                except Exception as e:
                    self.logger.error(f'Error creating request for {url}: {e}')

    def item_completed(self, results, item, info):
        """
        Called when all files for an item have been downloaded
        Stores metadata about the case and downloaded files
        """
        adapter = ItemAdapter(item)
        
        # Process download results
        file_paths = []
        failed_downloads = []
        
        for success, file_info in results:
            if success:
                file_paths.append(file_info['path'])
                self.logger.info(f"Downloaded: {file_info['path']}")
            else:
                # file_info is a Failure object when success=False
                failed_downloads.append(str(file_info))
                self.logger.error(f"Failed to download: {file_info}")
        
        # Store file paths in item
        adapter['file_paths'] = file_paths
        
        # Save metadata
        if file_paths or adapter.get('file_urls'):
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'case_number': adapter.get('case_number'),
                'case_title': adapter.get('case_title'),
                'case_url': adapter.get('case_url'),
                'case_status': adapter.get('case_status'),
                'court_name': adapter.get('court_name'),
                'judge_name': adapter.get('judge_name'),
                'parties': adapter.get('parties'),
                'requested_files': len(adapter.get('file_urls', [])),
                'downloaded_files': len(file_paths),
                'failed_downloads': len(failed_downloads),
                'file_paths': file_paths,
                'failed_urls': failed_downloads,
            }
            
            # Append to metadata file (JSONL format for easy streaming)
            try:
                with open(self.metadata_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(metadata, ensure_ascii=False) + '\n')
                self.logger.info(f"Metadata saved for case: {adapter.get('case_number')}")
            except Exception as e:
                self.logger.error(f"Failed to save metadata: {e}")
        
        # Drop item if no files were found or downloaded
        if not adapter.get('file_urls'):
            raise DropItem(f"No files found for case {adapter.get('case_number')}")
        
        return item

    def file_download_error(self, failure):
        """Handle file download errors"""
        self.logger.error(f'File download failed: {failure.request.url}')
        self.logger.error(f'Error details: {failure.value}')
        return failure


class DocumentMetadataExporter:
    """
    Helper class to export document metadata and create summary reports
    """
    
    def __init__(self, metadata_file):
        self.metadata_file = metadata_file
        self.logger = logging.getLogger(self.__class__.__name__)

    def read_metadata(self):
        """Read all metadata records (JSONL format)"""
        records = []
        if not os.path.exists(self.metadata_file):
            self.logger.warning(f'Metadata file not found: {self.metadata_file}')
            return records
        
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))
        except Exception as e:
            self.logger.error(f'Error reading metadata: {e}')
        
        return records

    def generate_report(self, output_file=None):
        """Generate a summary report of all downloads"""
        records = self.read_metadata()
        
        if not records:
            self.logger.info('No metadata records found')
            return
        
        report = {
            'generated': datetime.now().isoformat(),
            'total_cases': len(records),
            'total_files_requested': sum(r.get('requested_files', 0) for r in records),
            'total_files_downloaded': sum(r.get('downloaded_files', 0) for r in records),
            'total_failures': sum(r.get('failed_downloads', 0) for r in records),
            'success_rate': None,
            'cases': records
        }
        
        # Calculate success rate
        if report['total_files_requested'] > 0:
            report['success_rate'] = (
                report['total_files_downloaded'] / report['total_files_requested'] * 100
            )
        
        # Save report
        if output_file is None:
            output_file = 'downloads/report.json'
        
        try:
            os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            self.logger.info(f'Report saved to: {output_file}')
            return report
        except Exception as e:
            self.logger.error(f'Error saving report: {e}')
            return report

    def export_csv(self, output_file=None):
        """Export metadata as CSV"""
        import csv
        
        records = self.read_metadata()
        if not records:
            self.logger.info('No metadata records found')
            return
        
        if output_file is None:
            output_file = 'downloads/documents.csv'
        
        try:
            os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = [
                    'timestamp', 'case_number', 'case_title', 'case_status',
                    'court_name', 'judge_name', 'parties',
                    'requested_files', 'downloaded_files', 'failed_downloads'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for record in records:
                    row = {k: record.get(k) for k in fieldnames}
                    writer.writerow(row)
            
            self.logger.info(f'CSV exported to: {output_file}')
        except Exception as e:
            self.logger.error(f'Error exporting CSV: {e}')

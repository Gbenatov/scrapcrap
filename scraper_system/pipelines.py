"""
Custom Scrapy Pipelines for Court Document Scraping
Handles file download integration and document metadata storage
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import requests


class CourtDocumentPipeline:
    """
    Custom pipeline for storing document metadata
    Downloads files and tracks them
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.store_dir = None
        self.metadata_file = None
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def open_spider(self, spider):
        """Initialize when spider opens"""
        self.store_dir = 'downloads/court_documents'
        os.makedirs(self.store_dir, exist_ok=True)
        
        self.metadata_file = os.path.join(self.store_dir, 'metadata.jsonl')
        self.logger.info(f'Storage directory: {self.store_dir}')
        self.logger.info(f'Metadata file: {self.metadata_file}')

    def process_item(self, item, spider):
        """Process each item"""
        adapter = ItemAdapter(item)
        
        # Extract case information
        case_number = adapter.get('case_number', 'unknown')
        case_dir = os.path.join(self.store_dir, f'case_{case_number}')
        os.makedirs(case_dir, exist_ok=True)
        
        # Download files
        file_urls = adapter.get('file_urls', [])
        downloaded_files = []
        failed_downloads = []
        
        for file_url in file_urls:
            try:
                if isinstance(file_url, str) and file_url.strip():
                    filename = file_url.split('/')[-1]
                    if not filename or len(filename) < 3:
                        filename = f'document_{len(downloaded_files)}.pdf'
                    
                    file_path = os.path.join(case_dir, filename)
                    
                    # Download file
                    response = requests.get(file_url, timeout=30)
                    if response.status_code == 200:
                        with open(file_path, 'wb') as f:
                            f.write(response.content)
                        downloaded_files.append(f'case_{case_number}/{filename}')
                        self.logger.info(f'Downloaded: {file_path}')
                    else:
                        self.logger.error(f'Failed to download {file_url}: HTTP {response.status_code}')
                        failed_downloads.append(file_url)
            except Exception as e:
                self.logger.error(f'Error downloading {file_url}: {e}')
                failed_downloads.append(file_url)
        
        # Save metadata
        if file_urls or downloaded_files:
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'case_number': case_number,
                'case_title': adapter.get('case_title', 'Unknown'),
                'case_url': adapter.get('case_url', ''),
                'case_status': adapter.get('case_status', ''),
                'requested_files': len(file_urls),
                'downloaded_files': len(downloaded_files),
                'failed_downloads': len(failed_downloads),
                'file_paths': downloaded_files,
                'failed_urls': failed_downloads,
            }
            
            try:
                with open(self.metadata_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(metadata, ensure_ascii=False) + '\n')
                self.logger.info(f"Metadata saved for case: {case_number}")
            except Exception as e:
                self.logger.error(f"Failed to save metadata: {e}")
        
        # Drop if no files
        if not file_urls and not downloaded_files:
            raise DropItem(f"No files found for case {case_number}")
        
        return item


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

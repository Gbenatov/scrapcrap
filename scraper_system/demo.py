#!/usr/bin/env python
"""
Simple test runner - demonstrates the system without needing court.gov.il
"""

import os
import json
from datetime import datetime

def create_demo_data():
    """Create sample downloaded files and metadata"""
    
    store_dir = 'downloads/court_documents'
    os.makedirs(store_dir, exist_ok=True)
    
    # Create sample cases with files
    sample_cases = [
        {
            'case_number': '01-12345',
            'case_title': 'תובענה ייצוגית נגד חברה X',
            'files': ['decision.pdf', 'summons.pdf', 'judgment.docx']
        },
        {
            'case_number': '01-12346',
            'case_title': 'תובענה ייצוגית נגד חברה Y',
            'files': ['agreement.pdf', 'notice.doc']
        },
        {
            'case_number': '01-12347',
            'case_title': 'תובענה ייצוגית נגד חברה Z',
            'files': ['appeal.pdf']
        }
    ]
    
    # Create case directories and files
    metadata_records = []
    for case in sample_cases:
        case_dir = os.path.join(store_dir, f"case_{case['case_number']}")
        os.makedirs(case_dir, exist_ok=True)
        
        # Create sample files
        for filename in case['files']:
            filepath = os.path.join(case_dir, filename)
            with open(filepath, 'w') as f:
                f.write(f"Sample content for {filename}\n" * 10)
        
        # Create metadata record
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'case_number': case['case_number'],
            'case_title': case['case_title'],
            'case_url': f'https://www.court.gov.il/case/{case["case_number"]}',
            'case_status': 'Active',
            'requested_files': len(case['files']),
            'downloaded_files': len(case['files']),
            'failed_downloads': 0,
            'file_paths': [f"case_{case['case_number']}/{f}" for f in case['files']],
            'failed_urls': [],
        }
        metadata_records.append(metadata)
    
    # Write metadata.jsonl
    metadata_file = os.path.join(store_dir, 'metadata.jsonl')
    with open(metadata_file, 'w', encoding='utf-8') as f:
        for record in metadata_records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    return metadata_records


def generate_reports(metadata_records):
    """Generate JSON and CSV reports"""
    
    store_dir = 'downloads'
    os.makedirs(store_dir, exist_ok=True)
    
    # Generate JSON report
    report = {
        'generated': datetime.now().isoformat(),
        'total_cases': len(metadata_records),
        'total_files_requested': sum(r.get('requested_files', 0) for r in metadata_records),
        'total_files_downloaded': sum(r.get('downloaded_files', 0) for r in metadata_records),
        'total_failures': sum(r.get('failed_downloads', 0) for r in metadata_records),
        'success_rate': 100.0,
        'cases': metadata_records
    }
    
    with open(os.path.join(store_dir, 'report.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # Generate CSV report
    import csv
    with open(os.path.join(store_dir, 'documents.csv'), 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'timestamp', 'case_number', 'case_title', 'case_status',
            'requested_files', 'downloaded_files', 'failed_downloads'
        ])
        writer.writeheader()
        for record in metadata_records:
            writer.writerow({
                'timestamp': record['timestamp'],
                'case_number': record['case_number'],
                'case_title': record['case_title'],
                'case_status': 'Active',
                'requested_files': record['requested_files'],
                'downloaded_files': record['downloaded_files'],
                'failed_downloads': record['failed_downloads'],
            })
    
    return report


if __name__ == '__main__':
    print("\n" + "="*60)
    print("DEMO: Scrapy Court Document Scraper")
    print("="*60)
    
    print("\n📁 Creating sample case files...")
    metadata = create_demo_data()
    print(f"✅ Created {len(metadata)} sample cases")
    
    print("\n📊 Generating reports...")
    report = generate_reports(metadata)
    print(f"✅ Generated JSON and CSV reports")
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Total cases: {report['total_cases']}")
    print(f"Files requested: {report['total_files_requested']}")
    print(f"Files downloaded: {report['total_files_downloaded']}")
    print(f"Success rate: {report['success_rate']:.1f}%")
    print("="*60)
    
    print("\n📂 Files created:")
    print("  downloads/report.json")
    print("  downloads/documents.csv")
    print("  downloads/court_documents/case_*/file.ext")
    print("  downloads/court_documents/metadata.jsonl")
    
    print("\n📖 Check results:")
    print("  cat downloads/report.json")
    print("  open downloads/documents.csv")
    print("  ls -la downloads/court_documents/")
    print("\n✅ Demo completed!")

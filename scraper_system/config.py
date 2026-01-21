"""
Configuration file for the scraper system
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Scraper Configuration
SCRAPER_CONFIG = {
    'base_url': 'https://www.court.gov.il/NGCS.Web.Site/HomePage.aspx',
    'timeout': 10,
    'retry_attempts': 3,
    'retry_delay': 5,  # seconds
}

# Output Configuration
OUTPUT_CONFIG = {
    'data_dir': './data',
    'csv_filename': 'cases.csv',
    'json_filename': 'cases.json',
    'report_filename': 'report.json',
}

# Browser Configuration (for Selenium)
BROWSER_CONFIG = {
    'headless': True,
    'no_sandbox': True,
    'disable_dev_shm_usage': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

# Data Fields to Extract
DATA_FIELDS = {
    'case_id': 'CaseID',
    'case_display_id': 'CaseDisplayIdentifier',
    'case_name': 'CaseName',
    'open_date': 'CaseOpenDate',
    'court_name': 'CourtName',
    'plaintiff_group': 'RepresentativeComplaintGroupName',
    'legal_question': 'LegalQuestion',
    'requested_aid': 'RequestedAID',
    'claim_amount': 'ClaimAmount',
    'is_appeal': 'isAppealCase',
    'documents': 'Docs',
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_file': './logs/scraper.log',
}

# Analysis Configuration
ANALYSIS_CONFIG = {
    'high_value_threshold': 10000000,  # 10 million
    'top_n_cases': 10,
}

# Create necessary directories
def ensure_directories():
    """Create necessary directories if they don't exist"""
    for dir_path in [OUTPUT_CONFIG['data_dir'], './logs']:
        os.makedirs(dir_path, exist_ok=True)


# Call on import
ensure_directories()

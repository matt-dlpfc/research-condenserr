import logging
from bs4 import BeautifulSoup, Tag
import re
from dataclasses import dataclass
from typing import List, Dict, Optional
from collections import defaultdict
from specialized_scrapers.clinical_trials.formatter import process_clinical_trial_data

@dataclass
class SectionIdentifiers:
    """Flexible identifiers for different sections of the clinical trial data."""
    id_patterns: List[str]
    class_patterns: List[str]
    text_patterns: List[str]

class DataExtractionError(Exception):
    """Custom exception for data extraction errors."""
    pass

class ClinicalTrialScraper:
    """Simplified and more flexible clinical trial data scraper."""
    
    def __init__(self):
        self.soup = None
        self.extracted_data = defaultdict(dict)
        self.errors = []

    def extract_data(self, html_content: str) -> str:
        """Extract and format clinical trial data into markdown tables."""
        try:
            self.soup = BeautifulSoup(html_content, 'html.parser')
            self.extracted_data.clear()
            
            # Extract all card sections
            cards = self.soup.find_all(class_='usa-card')
            
            all_tables = []  # Collect all tables across sections
            
            for card in cards:
                # Get section header
                header = card.find(class_='usa-card__heading')
                if not header:
                    continue
                    
                # Extract content
                content = card.find(class_='usa-card__body')
                if not content:
                    continue

                # Extract tables by matching table elements with _ngcontent attributes
                tables = content.find_all(lambda tag: tag.name == 'table' and 
                                    any('_ngcontent-' in attr for attr in tag.attrs))
                
                if tables:
                    section_tables = [self.extract_table_data(table) for table in tables]
                    all_tables.extend(section_tables)

            # Convert all tables to markdown format
            if all_tables:
                try:
                    return process_clinical_trial_data(all_tables)
                except Exception as e:
                    self.errors.append(f"Error formatting tables: {str(e)}")
                    return ""
            
            return ""

        except Exception as e:
            self.errors.append(f"Critical error during data extraction: {str(e)}")
            logging.error(f"Critical error during data extraction: {str(e)}")
            return ""

    def extract_table_data(self, table: Tag) -> Dict:
        """Simplified table data extraction."""
        data = {'headers': [], 'rows': []}
        
        try:
            # Extract headers
            headers = table.find_all(['th'])
            data['headers'] = [h.get_text(strip=True) for h in headers]
            
            # Extract rows
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td'])
                if cells:
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    data['rows'].append(row_data)
                    
            return data

        except Exception as e:
            self.errors.append(f"Error extracting table data: {str(e)}")
            return data

    def get_extraction_status(self) -> Dict:
        """Get the status of the data extraction process."""
        return {
            'success': len(self.errors) == 0,
            'errors': self.errors,
            'sections_found': list(self.extracted_data.keys()),
            'completeness': {
                section: bool(data) for section, data in self.extracted_data.items()
            }
        }


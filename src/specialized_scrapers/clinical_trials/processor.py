from typing import Dict, Optional, Union
from .api import fetch_trial_data, load_trial_data, process_trial_data
from .scraper import ClinicalTrialScraper
import re
import logging
from bs4 import BeautifulSoup

class ClinicalTrialProcessor:
    def __init__(self):
        self.scraper = ClinicalTrialScraper()
        
    def process_data(self, content: str, source_type: str) -> Optional[str]:
        """Process clinical trial data from various sources."""
        logging.info(f"ClinicalTrialProcessor.process_data called with source_type={source_type}")
        
        try:
            # Try API first if we have an NCT ID
            if source_type in ('api', 'json'):
                try:
                    json_data = fetch_trial_data(
                        nct_id=content if source_type == 'api' else None,
                        json_file=content if source_type == 'json' else None
                    )
                    trial_data = load_trial_data(json_data)
                    return process_trial_data(trial_data)
                except Exception as e:
                    logging.warning(f"API processing failed: {str(e)}. Falling back to HTML scraping.")
                    return self._process_html(content)
                    
            # HTML processing
            elif source_type == 'html':
                return self._process_html(content)
                
        except Exception as e:
            logging.error(f"Error processing clinical trial data: {str(e)}")
            return None
            
    def _process_html(self, html_content: str) -> Optional[str]:
        """Process HTML content with multiple parser attempts."""
        logging.info("Starting _process_html")
        try:
            # Try html.parser first
            logging.debug("Attempting to parse with html.parser")
            soup = BeautifulSoup(html_content, 'html.parser')
            result = self.scraper.extract_data(str(soup))
            
            if result:
                logging.info("Successfully extracted data using html.parser")
            else:
                logging.info("No data from html.parser, trying lxml parser...")
                soup = BeautifulSoup(html_content, 'lxml')
                result = self.scraper.extract_data(str(soup))
                
                if result:
                    logging.info("Successfully extracted data using lxml parser")
                else:
                    logging.warning("No data extracted from either parser")
                    
            return result
            
        except Exception as e:
            logging.error(f"HTML processing failed: {str(e)}", exc_info=True)
            return None
            
    def _detect_source_type(self, source: str) -> str:
        """Automatically detect the source type."""
        if re.match(r'NCT\d{8}', source):
            return 'api'
        elif source.endswith('.json'):
            return 'json'
        # Try to find NCT ID in HTML content
        elif '<html' in source.lower():
            nct_match = re.search(r'NCT\d{8}', source)
            if nct_match:
                return 'api'
        return 'html'

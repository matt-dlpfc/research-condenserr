import os
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from pathlib import Path
import re
import logging
from typing import Optional

from specialized_scrapers.clinical_trials import ClinicalTrialProcessor
from specialized_scrapers.task_types import TaskType, DataSource

class ResearchCondenser:
    def __init__(self, task_subdir):
        """Initialize the research condenser with a task-specific subdirectory."""
        # Base directories are relative to the project root
        base_path = Path(__file__).parent.parent
        self.html_folder = base_path / "data" / "html-files" / task_subdir
        self.output_folder = base_path / "data" / "output" / task_subdir
        
        # Set up logging to both file and console
        log_file = base_path / "logs" / f"{task_subdir}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        # Create directories if they don't exist
        self.html_folder.mkdir(parents=True, exist_ok=True)
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        logging.info(f"Initialized ResearchCondenser for task: {task_subdir}")
        logging.info(f"Using html-files directory: {self.html_folder}")
        logging.info(f"Using output directory: {self.output_folder}")
        
        # Initialize clinical trial scraper
        self.clinical_processor = ClinicalTrialProcessor()

    def extract_text_from_html(self, html_content, source_type=None):
        """Extract meaningful text content from HTML while preserving structure."""
        logging.info(f"Starting extract_text_from_html with source_type={source_type}")
        
        if source_type == 'clinicaltrials':
            logging.debug("Detected clinical trials source type")
            try:
                logging.debug("Attempting to process clinical trial HTML content")
                if not hasattr(self, 'clinical_processor'):
                    logging.error("clinical_processor not initialized!")
                    return self._standard_text_extraction(html_content)
                
                # Try to process with clinical trial processor
                result = self.clinical_processor.process_data(html_content, 'html')
                
                if result:
                    logging.info("Successfully processed clinical trial data")
                    return result
                
                logging.warning("Clinical trial processing returned no results, falling back to standard extraction")
                return self._standard_text_extraction(html_content)
                    
            except Exception as e:
                logging.error(f"Error processing clinical trial data: {str(e)}", exc_info=True)
                return self._standard_text_extraction(html_content)
        
        return self._standard_text_extraction(html_content)

    def process_url(self, url, source_type=None):
        """Process a single URL and return its text content."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return self.extract_text_from_html(response.text, source_type=source_type)
        except Exception as e:
            logging.error(f"Error processing URL {url}: {str(e)}")
            return None

    def process_html_file(self, html_file_path, source_type=None):
        """Process a single HTML file and return its text content."""
        logging.info(f"Starting process_html_file with source_type={source_type}")
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                logging.debug(f"Successfully read HTML file: {html_file_path}")
            
            result = self.extract_text_from_html(html_content, source_type=source_type)
            if result:
                logging.info("Successfully extracted text from HTML")
            else:
                logging.warning("No text extracted from HTML")
            return result
        except Exception as e:
            logging.error(f"Error processing HTML file {html_file_path}: {str(e)}", exc_info=True)
            return None

    def save_to_markdown(self, content, source_name):
        """Save content to a markdown file with the specified naming convention."""
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = f"{date_str}_{source_name}.md"
        file_path = self.output_folder / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logging.info(f"Successfully saved content to {filename}")
            return file_path
        except Exception as e:
            logging.error(f"Error saving markdown file: {str(e)}")
            return None

    def append_to_inputs_file(self, content, research_type):
        """Append content to an existing MY INPUTS file in the task output directory."""
        try:
            # Look for any existing MY INPUTS file in the output directory
            input_files = list(self.output_folder.glob("MY INPUTS - *.md"))
            
            if not input_files:
                raise FileNotFoundError(
                    f"No 'MY INPUTS' file found in {self.output_folder}. "
                    "Please create one before running the script."
                )
            
            if len(input_files) > 1:
                logging.warning(f"Multiple 'MY INPUTS' files found in {self.output_folder}. Using the first one.")
            
            # Use the first MY INPUTS file found
            filepath = input_files[0]
            
            # Append content to file
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write("\n\n# Scraped HTML\n\n")
                f.write(content)
            
            logging.info(f"Content appended to {filepath}")
            
            
        except Exception as e:
            logging.error(f"Error appending to inputs file: {e}")

    def _standard_text_extraction(self, html_content):
        """Extract meaningful text content from HTML while preserving structure."""
        logging.info("Starting standard text extraction")
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Log the structure being processed
        logging.debug(f"Processing HTML with {len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li', 'div']))} elements")
        
        # Extract text while preserving important structural elements
        content = []
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li', 'div']):
            if element.name.startswith('h'):
                # Convert HTML headers to Markdown headers
                level = int(element.name[1])
                content.append(f"{'#' * level} {element.get_text().strip()}\n")
            elif element.name == 'p':
                content.append(f"{element.get_text().strip()}\n\n")
            elif element.name in ['ul', 'ol']:
                for li in element.find_all('li', recursive=False):
                    content.append(f"- {li.get_text().strip()}\n")
                content.append("\n")
        
        # Join all text blocks
        text = "\n".join(content)
        
        # Clean up excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text

def process_clinical_data(condenser: ResearchCondenser, source_type: DataSource):
    if source_type == DataSource.API:
        # Handle API input
        print("Enter NCT IDs one per line. When finished, enter a blank line.")
        nct_ids = []
        while True:
            try:
                nct_id = input().strip()
                if not nct_id:
                    break
                if re.match(r'NCT\d{8}', nct_id):
                    nct_ids.append(nct_id)
                else:
                    print(f"Invalid NCT ID format: {nct_id}")
            except EOFError:
                break

        for nct_id in nct_ids:
            # Convert the NCT ID to string before processing
            content = condenser.clinical_processor.process_data(str(nct_id), 'api')
            if content:
                md_file = condenser.save_to_markdown(content, nct_id)
                if md_file:
                    condenser.append_to_inputs_file(content, "clinical_trial_api")
    else:
        # Handle URL or HTML processing
        process_general_data(condenser, source_type, source_type_override='clinicaltrials')

def process_general_data(condenser: ResearchCondenser, source_type: DataSource, source_type_override=None):
    logging.info(f"Starting process_general_data with source_type={source_type}, override={source_type_override}")
    
    if source_type == DataSource.URL:
        # Process URLs
        print("Enter URLs one per line. When finished, enter a blank line or press Ctrl+D (Unix) / Ctrl+Z (Windows).")
        print("You can also paste multiple URLs at once, with each URL on a new line.")
        urls = []
        while True:
            try:
                url = input().strip()
                if not url:
                    break
                urls.append(url)
            except EOFError:
                break
        
        for url in urls:
            content = condenser.process_url(url, source_type=source_type)
            if content:
                source_name = re.sub(r'[^\w\-_.]', '_', url.split('/')[-1])
                md_file = condenser.save_to_markdown(content, source_name)
                if md_file:
                    condenser.append_to_inputs_file(content, "url_research")

    elif source_type == DataSource.HTML:
        # Process HTML files from task-specific html-files subdirectory
        html_files = list(condenser.html_folder.glob('*.html'))
        
        if not html_files:
            logging.warning(f"No HTML files found in {condenser.html_folder}!")
            return
        
        logging.info(f"Found {len(html_files)} HTML files to process")
        
        for html_file in html_files:
            logging.info(f"Processing HTML file: {html_file}")
            content = condenser.process_html_file(html_file, source_type=source_type_override)
            if content:
                logging.info(f"Successfully extracted content from {html_file}")
                md_file = condenser.save_to_markdown(content, html_file.stem)
                if md_file:
                    condenser.append_to_inputs_file(content, "html_research")
            else:
                logging.error(f"Failed to extract content from {html_file}")

def main():
    # Get and validate task subdirectory
    task_subdir = input("Please enter the task name (e.g., 'company_A'): ").strip()
    
    try:
        condenser = ResearchCondenser(task_subdir)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nBefore proceeding, please ensure you have created:")
        print(f"1. data/html-files/{task_subdir}/")
        print(f"2. data/output/{task_subdir}/")
        return

    # Get task type
    while True:
        try:
            task_type_str = input("Enter task type (clinical/general): ").lower()
            task_type = TaskType.from_string(task_type_str)
            break
        except ValueError as e:
            print(e)

    # Get data source based on task type
    available_sources = DataSource.get_sources_for_task(task_type)
    while True:
        source_options = "/".join([s.value for s in available_sources])
        source_type_str = input(f"Select data source ({source_options}): ").lower()
        try:
            source_type = DataSource(source_type_str)
            if source_type not in available_sources:
                raise ValueError
            break
        except ValueError:
            print(f"Invalid source type. Please choose from: {source_options}")

    # Process based on task type and source
    if task_type == TaskType.CLINICAL:
        process_clinical_data(condenser, source_type)
    else:
        process_general_data(condenser, source_type)

if __name__ == "__main__":
    main()
import os
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from pathlib import Path
import re
import logging

class ResearchCondenser:
    def __init__(self, task_subdir):
        """Initialize the research condenser with a task-specific subdirectory.
        
        Args:
            task_subdir (str): Name of the task subdirectory (e.g., 'company_A')
        """
        # Base directories are relative to the project root
        base_path = Path(__file__).parent.parent
        self.html_folder = base_path / "data" / "html-files" / task_subdir
        self.output_folder = base_path / "data" / "output" / task_subdir
        
        # Set up logging
        logging.basicConfig(level=logging.INFO,
                          format='%(asctime)s - %(levelname)s - %(message)s')
        
        # Create directories if they don't exist
        self.html_folder.mkdir(parents=True, exist_ok=True)
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        logging.info(f"Initialized ResearchCondenser for task: {task_subdir}")
        logging.info(f"Using html-files directory: {self.html_folder}")
        logging.info(f"Using output directory: {self.output_folder}")

    def extract_text_from_html(self, html_content):
        """Extract meaningful text content from HTML while preserving structure."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style']):
            element.decompose()
        
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
            
        return ''.join(content)

    def process_url(self, url):
        """Process a single URL and return its text content."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return self.extract_text_from_html(response.text)
        except Exception as e:
            logging.error(f"Error processing URL {url}: {str(e)}")
            return None

    def process_html_file(self, html_file_path):
        """Process a single HTML file and return its text content."""
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            return self.extract_text_from_html(html_content)
        except Exception as e:
            logging.error(f"Error processing HTML file {html_file_path}: {str(e)}")
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

def main():
    # Get task-specific subdirectory from user
    task_subdir = input("Please enter the task name (e.g., 'company_A'): ").strip()
    
    try:
        # Initialize the condenser with task subdirectory
        condenser = ResearchCondenser(task_subdir)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nBefore proceeding, please ensure you have created:")
        print(f"1. data/html-files/{task_subdir}/")
        print(f"2. data/output/{task_subdir}/")
        return
    
    # Get input type from user
    input_type = input("Would you like to process URLs or HTML files? (url/html): ").lower()
    
    if input_type == 'url':
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
            content = condenser.process_url(url)
            if content:
                source_name = re.sub(r'[^\w\-_.]', '_', url.split('/')[-1])
                md_file = condenser.save_to_markdown(content, source_name)
                if md_file:
                    condenser.append_to_inputs_file(content, "url_research")
    
    elif input_type == 'html':
        # Process HTML files from task-specific html-files subdirectory
        html_files = list(condenser.html_folder.glob('*.html'))
        
        if not html_files:
            print(f"No HTML files found in {condenser.html_folder}!")
            return
        
        for html_file in html_files:
            content = condenser.process_html_file(html_file)
            if content:
                md_file = condenser.save_to_markdown(content, html_file.stem)
                if md_file:
                    condenser.append_to_inputs_file(content, "html_research")

if __name__ == "__main__":
    main()
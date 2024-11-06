import json
from typing import Dict, List, Any
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Section:
    title: str
    description: str = ""
    time_frame: str = ""
    population: str = ""
    tables: List[Dict] = None
    
    def __post_init__(self):
        if self.tables is None:
            self.tables = []

def extract_mean_sd(value: str) -> tuple:
    """Extract mean and standard deviation from string formats like '1.6(0)' or '1.6 (0)'."""
    if not value or value == '':
        return None, None
    try:
        parts = value.replace(' ', '').split('(')
        mean = float(parts[0])
        sd = float(parts[1].rstrip(')'))
        return mean, sd
    except:
        return value, None

def clean_value(value: str) -> str:
    """Clean and format numerical values."""
    if isinstance(value, (int, float)):
        return str(value)
    if not value or value.strip() == '':
        return ''
    return value.strip()

def clean_header(header: str) -> str:
    """Clean duplicated and malformatted headers."""
    if not header:
        return ""
    # Remove duplicated sections
    if "Period Title:" in header:
        cycle = header.split("Period Title:")[-1]
        if cycle.endswith(cycle):
            cycle = cycle[:len(cycle)//2]
        return cycle.strip()
    # Remove other common duplications
    if header.endswith(header[:int(len(header)/2)]):
        header = header[:int(len(header)/2)]
    return header.strip()

def format_description(desc: str) -> str:
    """Format long descriptions to be more readable."""
    if not desc or len(desc) < 100:  # Only process long descriptions
        return desc
    # Replace newlines with spaces and compact multiple spaces
    return ' '.join(desc.split())

def handle_footnotes(rows: List[List[str]]) -> tuple:
    """Separate footnotes from data rows and format them."""
    data_rows = []
    footnotes = []
    current_footnote_marker = 1
    footnote_mapping = {}
    
    for row in rows:
        if not row:
            continue
            
        if row[0] and '[' in row[0] and ']' in row[0]:
            # This is a footnote
            note_text = row[0].split(']')[1].split('[')[0]  # Extract the note text
            if note_text and not note_text.endswith(note_text):  # Remove duplicates
                note_text = note_text[:len(note_text)//2]
            if note_text.strip():
                footnotes.append(f"{current_footnote_marker}. {note_text.strip()}")
                footnote_mapping[row[0]] = current_footnote_marker
                current_footnote_marker += 1
        else:
            # Process data rows and replace footnote markers
            processed_row = []
            for cell in row:
                if '[' in str(cell) and ']' in str(cell):
                    for original, number in footnote_mapping.items():
                        cell = cell.replace(original, f"[{number}]")
                processed_row.append(cell)
            data_rows.append(processed_row)
            
    return data_rows, footnotes

def create_markdown_table(table_data: Dict, section_level: int = 2) -> str:
    """Create a markdown table with improved formatting."""
    headers = [clean_header(h) for h in table_data.get('headers', [])]
    rows, footnotes = handle_footnotes(table_data.get('rows', []))
    
    markdown = []
    current_cycle = None
    
    # Process rows
    for row in rows:
        if not row or all(not cell for cell in row):
            continue
            
        # Check for cycle headers
        first_cell = clean_header(row[0])
        if "Cycle" in first_cell:
            current_cycle = first_cell
            markdown.append(f"\n{'#' * section_level} {current_cycle}\n")
            continue
            
        # Format regular data rows
        cleaned_row = []
        for i, cell in enumerate(row):
            cell_value = clean_value(cell)
            if i == 0:  # First column special handling
                cell_value = clean_header(cell_value)
            elif len(str(cell_value)) > 100:
                cell_value = format_description(cell_value)
            cleaned_row.append(cell_value)
        
        # Add headers if this is the first data row
        if not markdown or (markdown[-1].startswith('#') and headers):
            markdown.extend([
                "| " + " | ".join(headers) + " |",
                "|" + "|".join("-" * max(len(h), 3) for h in headers) + "|"
            ])
        
        # Add the data row
        if cleaned_row:
            markdown.append("| " + " | ".join(
                str(cell) for cell in (cleaned_row + [''] * (len(headers) - len(cleaned_row)))
            ) + " |")
    
    # Add footnotes if any
    if footnotes:
        markdown.extend(["\n**Footnotes:**"] + footnotes)
    
    return "\n".join(markdown)

def parse_trial_data(data_list: List[Dict]) -> List[Section]:
    """Parse clinical trial data into organized sections."""
    sections = []
    current_section = None
    
    for data in data_list:
        # Handle metadata
        if not data.get('headers') and data.get('rows'):
            for row in data['rows']:
                if len(row) >= 2:
                    if row[0] == 'Description':
                        if current_section:
                            sections.append(current_section)
                        current_section = Section(title="")
                        current_section.description = row[1]
                    elif row[0] == 'Time Frame':
                        if current_section:
                            current_section.time_frame = row[1]
                    elif row[0] == 'Analysis Population Description':
                        if current_section:
                            current_section.population = row[1]
        
        # Handle data tables
        elif data.get('headers') or data.get('rows'):
            if not current_section:
                current_section = Section(title="Results")
            if data.get('rows'):
                current_section.tables.append(data)
    
    if current_section:
        sections.append(current_section)
    
    return sections

def process_clinical_trial_data(data_list: List[Dict]) -> str:
    """Main function to process clinical trial data and convert to markdown."""
    sections = parse_trial_data(data_list)
    markdown = []
    
    for section in sections:
        if section.title:
            markdown.append(f"# {section.title}\n")
        if section.description:
            markdown.append(f"## Description\n{section.description}\n")
        if section.time_frame:
            markdown.append(f"## Time Frame\n{section.time_frame}\n")
        if section.population:
            markdown.append(f"## Analysis Population\n{section.population}\n")
        
        # Process tables
        for table in section.tables:
            markdown.append(create_markdown_table(table))
            markdown.append("\n")  # Add spacing between tables
    
    return "\n".join(markdown)


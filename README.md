# Research Condenser Documentation

## Overview
Research Condenserr is a Python tool designed to extract and format research data from various sources, with specialized support for clinical trials data. It processes HTML content (either from files or URLs) and converts it into well-formatted markdown documents, ready to be integrated in other workflows.

## Core Components

### 1. Research Condenser Class
Location: `src/research_condenser.py`

The main class that handles:
- HTML content processing
- File management
- Text extraction
- Markdown conversion

Key methods:
- `extract_text_from_html()`: Converts HTML to structured text
- `process_url()`: Handles URL-based content
- `process_html_file()`: Processes local HTML files
- `save_to_markdown()`: Saves extracted content as markdown
- `append_to_inputs_file()`: Adds content to a master input file

### 2. Clinical Trial Processing
Location: `src/specialized_scrapers/clinical_trials.py`

Specialized scraper for clinical trials data that:
- Extracts structured data from clinical trial pages
- Processes complex table structures
- Converts trial data to markdown format

### 3. Clinical Trial Table Formatting
Location: `src/specialized_scrapers/clinical_trial_tables_to_markdown.py`

Handles the conversion of clinical trial tables, specifically "Outcome results" and "Adverse effects", to markdown format with:
- Table structure preservation
- Footnote handling
- Section organization
- Data cleaning

## Installation

1. Clone the repository:
```bash
git clone https://github.com/matt-dlpfc/research-condenserr.git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

1. Create required directories:
```
data/
├── html-files/
│   └── [task_name]/
└── output/
    └── [task_name]/
```

2. Run the script:
```bash
python src/research_condenser.py
```

### Input Options

1. **URL Processing**
   - Choose 'url' when prompted
   - Enter URLs one per line
   - End input with blank line or Ctrl+D/Ctrl+Z

2. **HTML File Processing**
   - Place HTML files in `data/html-files/[task_name]/`
   - Choose 'html' when prompted
   - Script processes all HTML files in directory

### Source Type Options

- Clinical Trials Data
  - Answer 'yes' when prompted about clinicaltrials.gov
  - Uses specialized scraper for clinical trial data
  - Preserves table structures and metadata

- General HTML Content
  - Answer 'no' for standard HTML processing
  - Uses general-purpose text extraction

## Output

The script generates:
1. Individual markdown files for each processed source
2. Appends content to a master "MY INPUTS" file
3. Organized by task in the output directory

## Directory Structure

```
research-condenserr/
├── src/
│   ├── research_condenser.py
│   └── specialized_scrapers/
│       ├── clinical_trials.py
│       └── clinical_trial_tables_to_markdown.py
├── data/
│   ├── html-files/
│   └── output/
├── requirements.txt
└── README.md
```

## Error Handling

The script includes comprehensive error handling:
- Logs errors to console
- Continues processing remaining files if one fails
- Creates detailed error messages for debugging

## Contributing

Pull requests are welcome. For major changes:
1. Open an issue first
2. Discuss proposed changes
3. Submit pull request

## License

[MIT License](https://choosealicense.com/licenses/mit/)
## Changelog
Recent changes:
* Update readme (2024-11-06)
* Update changelog (2024-11-06)
* Update changelog with recent changes (2024-11-06)

For full changelog, see [CHANGELOG.md](CHANGELOG.md)

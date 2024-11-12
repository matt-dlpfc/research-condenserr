# Research Condenser

The Research Condenser is a Python application designed to extract, process, and save **qualitative and ad-hoc** research that you, fellow analyst, carried out to answer some questions. In other words, this is meant to act as a helpful research condenser. This README provides an overview of the functionality, usage, and methods available in the codebase.

## Sort of vision
My vision for this mini-project is to create a modular framework that can act on 1) simple, general research tasks such as individual competitor analysis, sense-making; 2) specialized data collection and synthesis tasks/use cases (e.g. clinical trial data).

Right now, the "synthesis" capability is not part of this mini-project, but a minimum version will be implemented soon. In the future, I want keep adding #2 (ability to handle specialized use cases) based on how useful they are to me. I am pondering whether to add an extremely simplistic roadmap in this file.

## Important disclaimers
1) This mini-project is **NOT** intended to be used for quantitative data or to populate relational databases, or similar. You'll be disappointed if you try to do so. Or, I'll be very surprised to hear otherwise (I hope for the latter!).
2) By "research" I do not mean scientific or academic research; rather, I refer to stuff like market research, individual competitor analysis, market trend analysis, sense-making of an event or specific topic, getting some insights about a specific clinical trial, and so on.

## Table of (remaining) contents
- [Usage](#usage)
- [Execution Logic](#execution-logic)
- [Methods](#methods)
- [Directory structure](#directory-structure)
- [Logging](#logging)
- [Installation](#installation)
- [License](#license)
- [Contributing](#contributing)
## Usage
To run the application, execute the following command in your terminal:

```
python src/research_condenser.py
```

You will be prompted to enter a task name and select a task type (clinical/general) and data source (HTML, URL, API).

## Execution Logic

1. **Initialization**: The application initializes a `ResearchCondenser` instance with a task-specific subdirectory for storing HTML files and output data.

2. **Task Type Selection**: Users can choose between clinical and general tasks, which determine the processing logic.

3. **Data Source Selection**: Depending on the task type, users can select from available data sources:
   - HTML: Process HTML files from a specified directory.
   - URL: Extract data from provided URLs.
   - API: Fetch clinical trial data using NCT IDs.

4. **Data Processing**: The application processes the selected data source, extracts relevant information, and saves it in markdown format.

5. **Logging**: Throughout the execution, the application logs important events and errors for debugging and tracking purposes.

## Methods

### ResearchCondenser

- `__init__(self, task_subdir)`: Initializes the ResearchCondenser with a specified task subdirectory for storing HTML files and output data.

- `extract_text_from_html(self, html_content, source_type=None)`: Extracts meaningful text content from HTML while preserving structure. It uses specialized processors for clinical trial data if the source type is specified.

- `process_url(self, url, source_type=None)`: Processes a single URL and returns its text content.

- `process_html_file(self, html_file_path, source_type=None)`: Processes a single HTML file and returns its text content.

- `save_to_markdown(self, content, source_name)`: Saves extracted content to a markdown file with a specified naming convention.

- `append_to_inputs_file(self, content, research_type)`: Appends content to an existing "MY INPUTS" file in the task output directory.

- `_standard_text_extraction(self, html_content)`: Performs standard text extraction from HTML content.

### ClinicalTrialProcessor

- `process_data(self, content: str, source_type: str)`: Processes clinical trial data from various sources (API, JSON, HTML) and returns formatted markdown.

### ClinicalTrialScraper

- `extract_data(self, html_content: str) -> str`: Extracts and formats clinical trial data into markdown tables from the provided HTML content.

### DataSource Enum

- `get_sources_for_task(cls, task_type: TaskType)`: Returns a list of available data sources based on the selected task type.

## Directory Structure

```
research-condenserr/
│
├── data/
│   ├── html-files/
│   │   └── <task_subdir>/          # Directory for HTML files specific to tasks
│   └── output/
│       └── <task_subdir>/          # Directory for output files specific to tasks
│
├── logs/                            # Directory for log files
│   └── <task_subdir>_<timestamp>.log
│
├── src/
│   ├── research_condenser.py        # Main script for the Research Condenser
│   └── specialized_scrapers/
│       ├── clinical_trials/
│       │        ├── __init__.py          # Package initialization
│       │         ├── api.py               # API handling for clinical trials
│       │         ├── formatter.py          # Formatting functions for clinical trial data
│       │         ├── processor.py          # Processing logic for clinical trial data
│       │         └── scraper.py            # Scraping logic for clinical trial data
│       └── task_types.py             # Task type and data source enumerations
│
└── requirements.txt                  # List of dependencies for the project
```
## Logging

The application uses Python's built-in logging module to log events and errors. Logs are saved to a file in the `logs` directory and are also printed to the console. The log file is named based on the task subdirectory and the current timestamp.


## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```


## License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/). See the LICENSE file for more details.

## Contributing

Contributions are not expected, but if you do want to contribute, who am I to prevent you from doing that? Please submit a pull request or open an issue for any enhancements or bug fixes.

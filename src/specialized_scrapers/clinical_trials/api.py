import json
from typing import Dict, List, Any, Union
from dataclasses import dataclass
from tabulate import tabulate
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
import requests

@dataclass
class TrialData:
    description_module: Dict
    outcomes_module: Dict
    outcome_measures_module: Dict
    adverse_events_module: Dict

def load_trial_data(json_data: Union[str, Dict]) -> TrialData:
    """Load and parse the JSON data into a TrialData object"""
    if isinstance(json_data, dict):
        data = json_data
    else:
        data = json.loads(json_data)
    
    protocol_section = data.get('protocolSection', {})
    results_section = data.get('resultsSection', {})
    
    return TrialData(
        description_module=protocol_section.get('descriptionModule', {}),
        outcomes_module=protocol_section.get('outcomesModule', {}),
        outcome_measures_module=results_section.get('outcomeMeasuresModule', {}),
        adverse_events_module=results_section.get('adverseEventsModule', {})
    )

def process_description_module(description_module: Dict) -> str:
    """Process the description module into formatted text"""
    output = []
    if 'briefSummary' in description_module:
        output.append("Brief Summary:")
        output.append(description_module['briefSummary'])
        output.append("")
    
    if 'detailedDescription' in description_module:
        output.append("Detailed Description:")
        output.append(description_module['detailedDescription'])
    
    return "\n".join(output)

def process_outcomes_module(outcomes_module: Dict) -> pd.DataFrame:
    """Convert outcomes module into a pandas DataFrame"""
    outcomes = []
    
    for outcome_type in ['primaryOutcomes', 'secondaryOutcomes']:
        if outcome_type in outcomes_module:
            for outcome in outcomes_module[outcome_type]:
                outcomes.append({
                    'Type': 'Primary' if outcome_type == 'primaryOutcomes' else 'Secondary',
                    'Measure': outcome.get('measure', ''),
                    'Description': outcome.get('description', ''),
                    'Time Frame': outcome.get('timeFrame', '')
                })
    
    return pd.DataFrame(outcomes)

def process_outcome_measure(measure: Dict) -> tuple[str, pd.DataFrame]:
    """Process a single outcome measure into context text and data table"""
    context = f"""
Type: {measure.get('type', '')}
Description: `{measure.get('description', '')}`
Population: {measure.get('populationDescription', '')}
Status: {measure.get('reportingStatus', '')}
Parameter Type: {measure.get('paramType', '')}
Unit: `{measure.get('unitOfMeasure', '')}`
Time Frame: {measure.get('timeFrame', '')}

"""
    
    # Create DataFrame from measurements
    data = []
    if 'classes' in measure:
        for class_item in measure['classes']:
            class_title = class_item.get('title', '')
            if 'categories' in class_item:
                for category in class_item['categories']:
                    if 'measurements' in category:
                        for measurement in category['measurements']:
                            row = {
                                'Class': class_title,
                                'Group': measurement.get('groupId', ''),
                                'Value': measurement.get('value', ''),
                                'Spread': measurement.get('spread', '')
                            }
                            data.append(row)
    
    return context.strip(), pd.DataFrame(data)

def process_adverse_events(adverse_events: Dict) -> tuple[str, List[pd.DataFrame]]:
    """Process adverse events module into context and multiple tables"""
    context = f"""
Time Frame: {adverse_events.get('timeFrame', '')}
Frequency Threshold: {adverse_events.get('frequencyThreshold', '')}

"""
    
    # Create summary table of event groups
    summary_data = []
    if 'eventGroups' in adverse_events:
        for group in adverse_events['eventGroups']:
            summary_data.append({
                'Group': group.get('title', ''),
                'Description': group.get('description', ''),
                'Deaths Affected/At Risk': f"{group.get('deathsNumAffected', 0)}/{group.get('deathsNumAtRisk', 0)}",
                'Serious Affected/At Risk': f"{group.get('seriousNumAffected', 0)}/{group.get('seriousNumAtRisk', 0)}",
                'Other Affected/At Risk': f"{group.get('otherNumAffected', 0)}/{group.get('otherNumAtRisk', 0)}"
            })
    
    summary_df = pd.DataFrame(summary_data)
    
    return context.strip(), [summary_df]

def process_trial_data(trial_data: TrialData) -> str:
    """Process trial data and return formatted markdown string"""
    output = []
    
    # Process Description Module
    output.append("# Description Module")
    output.append(process_description_module(trial_data.description_module))
    output.append("\n")
    
    # Process Outcomes Module
    output.append("# Outcomes Module")
    outcomes_df = process_outcomes_module(trial_data.outcomes_module)
    output.append(tabulate(outcomes_df, headers='keys', tablefmt='pipe'))
    output.append("\n")
    
    # Process Outcome Measures Module
    output.append("# Outcome Measures Module")
    if 'outcomeMeasures' in trial_data.outcome_measures_module:
        for measure in trial_data.outcome_measures_module['outcomeMeasures']:
            context, data = process_outcome_measure(measure)
            output.append(f"## `{measure.get('title', 'Untitled Outcome Measure')}`\n")
            output.append(f"\n{context}\n")
            output.append(tabulate(data, headers='keys', tablefmt='pipe'))
            output.append("\n")
    
    # Process Adverse Events Module
    output.append("# Adverse Events Module\n")
    context, tables = process_adverse_events(trial_data.adverse_events_module)
    output.append(f"\n{context}\n")
    for table in tables:
        output.append(tabulate(table, headers='keys', tablefmt='pipe'))
    
    return "\n".join(output)

def fetch_trial_data(nct_id=None, json_file=None) -> Dict:
    """Fetch trial data either from API or local JSON file"""
    if nct_id:
        url = f"https://clinicaltrials.gov/api/v2/studies/{nct_id}?format=json&markupFormat=markdown&fields=OutcomeMeasuresModule|AdverseEventsModule|LimitationsAndCaveats|DescriptionModule|OutcomesModule"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from API: {str(e)}")
            sys.exit(1)
    
    elif json_file:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading JSON file: {str(e)}")
            sys.exit(1)
    
    else:
        print("Error: Either NCT ID or JSON file path must be provided")
        sys.exit(1)

def main():
    """Main function to process trial data from JSON file or API and write to markdown"""
    if len(sys.argv) != 2:
        print("Usage: python process_api.py <NCT_ID or path_to_json_file>")
        sys.exit(1)
    
    input_value = sys.argv[1]
    
    try:
        # Fetch data either from API or local file
        if input_value.startswith("NCT"):
            data = fetch_trial_data(nct_id=input_value)
        else:
            data = fetch_trial_data(json_file=input_value)
        
        # Process data
        trial_data = TrialData(
            description_module=data.get('protocolSection', {}).get('descriptionModule', {}),
            outcomes_module=data.get('protocolSection', {}).get('outcomesModule', {}),
            outcome_measures_module=data.get('resultsSection', {}).get('outcomeMeasuresModule', {}),
            adverse_events_module=data.get('resultsSection', {}).get('adverseEventsModule', {})
        )
        
        markdown_output = process_trial_data(trial_data)
        
        # Create output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(f"trial_results_{timestamp}.md")
        
        # Write to markdown file with UTF-8 encoding
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_output)
        
        print(f"Results written to: {output_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
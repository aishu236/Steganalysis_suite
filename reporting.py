import json
from datetime import datetime
import os  # Import the 'os' module

def generate_report(input_file, analysis_results):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = f"steganalysis_report_{os.path.basename(input_file)}_{timestamp}.json"

    report_data = {
        "input_file": input_file,
        "timestamp": timestamp,
        "analysis_results": analysis_results
    }

    try:
        with open(report_filename, 'w') as f:
            json.dump(report_data, f, indent=4)
        print(f"Report saved to: {report_filename}")
    except Exception as e:
        print(f"Error saving report: {e}")

    print("\n--- Analysis Report ---")
    print(f"Input File: {input_file}")
    print(f"Timestamp: {timestamp}")
    print("\nAnalysis Results:")
    print(json.dumps(analysis_results, indent=4))
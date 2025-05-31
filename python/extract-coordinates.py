import csv
import sys
import re
from xml.etree import ElementTree as ET

def extract_plot_data(xml_file, output_csv):
    """Extract plot data from XML with Plot_N tags and write to CSV"""
    try:
        # Parse the XML file
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Prepare CSV output
        with open(output_csv, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, 
                                  fieldnames=['Latitude', 'Longitude', 'Grid', 'Releve'],
                                  extrasaction='ignore')
            writer.writeheader()
            
            extracted_count = 0
            
            # Find all elements that match Plot_ followed by digits
            for element in root.iter():
                if re.match(r'^Plot_\d+$', element.tag):
                    try:
                        data = {
                            'Latitude': element.get('northing_lat'),
                            'Longitude': element.get('easting_lon'),
                            'Grid': element.get('custom_a_plots'),
                            'Releve': element.get('name')
                        }
                        
                        # Only write if we have all required fields
                        if all(data.values()):
                            writer.writerow(data)
                            extracted_count += 1
                        else:
                            missing = [k for k, v in data.items() if not v]
                            print(f"Warning: Missing attributes in {element.tag}: {', '.join(missing)}")
                            
                    except Exception as e:
                        print(f"Error processing {element.tag}: {str(e)}")
            
            print(f"\nExtraction complete. Found {extracted_count} valid plots.")
            if extracted_count == 0:
                print("No valid records found. Check if:")
                print("- XML contains Plot_N tags")
                print("- Tags have all required attributes")
                if len(list(root.iter())) > 0:
                    sample_tag = next(root.iter()).tag
                    print(f"First tag found: {sample_tag}")
    
    except ET.ParseError:
        print("Error: Invalid XML file format")
    except FileNotFoundError:
        print(f"Error: File {xml_file} not found")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract_plots.py <input.xml> <output.csv>")
        print("Example: python extract_plots.py survey_data.xml plot_coordinates.csv")
        sys.exit(1)

extract_plot_data(sys.argv[1], sys.argv[2]) 

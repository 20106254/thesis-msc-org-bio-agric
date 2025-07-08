import csv
import sys
import re
from xml.etree import ElementTree as ET

species_count = {
    72: 21,
    74: 20,
    75: 20,
    76: 19,
    78: 19,
    83: 19,
    59: 18,
    63: 18,
    51: 17,
    73: 17,
    66: 16,
    71: 16,
    52: 15,
    53: 15,
    60: 15,
    62: 15,
    67: 15,
    68: 15,
    69: 15,
    77: 15,
    79: 15,
    55: 14,
    64: 14,
    70: 14,
    50: 13,
    54: 13,
    58: 13,
    80: 13,
    82: 13,
    56: 12,
    61: 12,
    57: 11,
    31: 10,
    40: 10,
    65: 10,
    8: 9,
    30: 8,
    33: 8,
    38: 8,
    41: 8,
    46: 8,
    48: 8,
    81: 8,
    2: 7,
    3: 7,
    28: 7,
    36: 7,
    39: 7,
    47: 7,
    49: 7,
    1: 6,
    5: 6,
    32: 6,
    35: 6,
    44: 6,
    45: 6,
    9: 5,
    42: 5,
    43: 5,
    4: 4,
    6: 4,
    10: 4,
    37: 4,
    7: 3,
    34: 3
}

def extract_plot_data(xml_file, output_csv):
    """Extract plot data from XML with Plot_N tags and write to CSV"""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        with open(output_csv, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile,
                                  fieldnames=['Latitude', 'Longitude', 'Grid', 'Releve', 'pH', 'SpeciesCount','Date'],
                                  extrasaction='ignore')
            writer.writeheader()

            extracted_count = 0

            for element in root.iter():
                if re.match(r'^Plot_\d+$', element.tag):
                    try:
                        releve_id = element.get('name')
                        data = {
                            'Latitude': element.get('northing_lat'),
                            'Longitude': element.get('easting_lon'),
                            'Grid': element.get('custom_a_plots'),
                            'Releve': releve_id,
                            'pH' : element.get('custom_d_plots'),
                            'SpeciesCount': None,
                            'Date': element.get('date')
                        }

                        if all([data['Latitude'], data['Longitude'], data['Grid'], data['Releve']]):
                            try:
                                releve_num = int(releve_id)
                                data['SpeciesCount'] = species_count.get(releve_num, "N/A")
                            except ValueError:
                                data['SpeciesCount'] = "N/A"
                            
                            writer.writerow(data)
                            extracted_count += 1
                        else:
                            missing = [k for k, v in data.items() if not v and k != 'SpeciesCount']
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

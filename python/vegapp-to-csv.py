import xml.etree.ElementTree as ET
import csv
import argparse
import sys

def parse_xml_and_write_csv(input_file, output_file):
    try:
        tree = ET.parse(input_file)
        root = tree.getroot()

        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['RELEVE_ID', 'SPECIES_NAME', 'GRID_NO', 'DOMIN']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            plots = root.find('.//Plots')
            if plots is not None:
                for plot in plots:
                    plot_name = plot.get('name', '')
                    
                    if plot_name == "22":
                        continue
                        
                    custom_d = plot.get('custom_d_plots', '')

                    species_list = plot.find('.//Species')
                    if species_list is not None:
                        for species in species_list:
                            genus = species.get('genus', '')
                            spec = species.get('spec', '')
                            quantity_id = species.get('quantity_id', '')

                            if not quantity_id:
                                continue

                            species_name = f"{genus} {spec}" if genus and spec else ''

                            writer.writerow({
                                'RELEVE_ID': plot_name,
                                'SPECIES_NAME': species_name,
                                'GRID_NO': custom_d,
                                'DOMIN': quantity_id
                            })
        print(f"Successfully extracted data to {output_file}")
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"File error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Extract plot and species data from XML to CSV')
    parser.add_argument('input_file', help='Path to the input XML file')
    parser.add_argument('output_file', help='Path to the output CSV file')
    
    args = parser.parse_args()
    
    parse_xml_and_write_csv(args.input_file, args.output_file)

if __name__ == '__main__':
    main()

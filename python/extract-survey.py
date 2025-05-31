import csv
import sys
import re

def parse_grid_range(grid_range):
    """Parse grid range string like 'G2-G5' into (min_grid, max_grid)"""
    match = re.match(r'G(\d+)-G(\d+)$', grid_range, re.IGNORECASE)
    if not match:
        raise ValueError("Grid range must be in format 'GX-GY' where X and Y are numbers")
    min_grid = int(match.group(1))
    max_grid = int(match.group(2))
    return sorted([min_grid, max_grid])  # Ensure proper order

def extract_surveys(input_file, grid_range):
    """Extract surveys within grid range while preserving original formatting"""
    min_grid, max_grid = parse_grid_range(grid_range)
    extracted = []
    original_header = None
    original_dialect = None
    
    with open(input_file, 'r', newline='') as f:
        # Sniff the CSV dialect to preserve original formatting
        dialect = csv.Sniffer().sniff(f.read(1024))
        f.seek(0)
        reader = csv.reader(f, dialect)
        original_header = next(reader)  # Save header
        
        # Find GRID_NO column index
        try:
            grid_col = original_header.index('GRID_NO')
        except ValueError:
            raise ValueError("Input file missing required GRID_NO column")
        
        for row in reader:
            try:
                grid_no = int(row[grid_col])
                if min_grid <= grid_no <= max_grid:
                    extracted.append(row)
            except (ValueError, IndexError):
                continue  # Skip rows with invalid GRID_NO
    
    if not extracted:
        print(f"No records found in grid range G{min_grid}-G{max_grid}")
        return
    
    # Write output preserving original format
    output_file = f"{input_file[:-4]}_G{min_grid}-G{max_grid}.csv"
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f, dialect=dialect)  # Use original dialect
        writer.writerow(original_header)
        writer.writerows(extracted)
    
    print(f"Extracted {len(extracted)} records to {output_file}")
    print(f"Preserved original file format including:")
    print(f"- Delimiter: '{dialect.delimiter}'")
    print(f"- Quote character: '{dialect.quotechar}'")
    print(f"- Line terminator: {repr(dialect.lineterminator)}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python extract_survey.py <input_file.csv> <grid_range>")
        print("Example: python extract_survey.py vegetation_data.csv G2-G5")
        sys.exit(1)
    
    try:
        extract_surveys(sys.argv[1], sys.argv[2])
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

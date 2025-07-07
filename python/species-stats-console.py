import csv
import sys
from collections import defaultdict

def count_species_per_releve(file_path):
    """Count the number of species in each relevé."""
    species_per_releve = defaultdict(set)
    
    try:
        with open(file_path, mode='r') as csvfile:
            reader = csv.DictReader(csvfile)
            if not all(field in reader.fieldnames for field in ['RELEVE_ID', 'SPECIES_NAME']):
                raise ValueError("CSV file must contain RELEVE_ID and SPECIES_NAME columns")
                
            for row in reader:
                releve_id = row['RELEVE_ID']
                species_name = row['SPECIES_NAME']
                species_per_releve[releve_id].add(species_name)
                
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not species_per_releve:
        print("Error: No valid data found in the file.", file=sys.stderr)
        sys.exit(1)
    
    return species_per_releve

def print_species_count_table(species_per_releve):
    """Print a formatted table sorted HIGH to LOW by species count."""
    # Convert to list of (RELEVE_ID, count) tuples and sort by count (descending)
    sorted_counts = sorted(
        [(releve_id, len(species)) for releve_id, species in species_per_releve.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    # Header
    print(f"{'RELEVE_ID':<15} {'Number of Species':>15}")
    print("-" * 30)
    
    # Rows (now sorted high-to-low)
    for releve_id, count in sorted_counts:
        print(f"{releve_id:<15} {count:>15}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python species_count.py <input_file.csv>", file=sys.stderr)
        sys.exit(1)
    
    file_path = sys.argv[1]
    species_per_releve = count_species_per_releve(file_path)
    print_species_count_table(species_per_releve)

if __name__ == "__main__":
    main()

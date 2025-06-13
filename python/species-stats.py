import csv
import sys
from collections import defaultdict

def analyze_species_data(file_path):
    """Analyze species data and return comprehensive statistics."""
    species_scores = defaultdict(float)
    unique_species = set()
    species_per_releve = defaultdict(set)
    unique_releve_ids = set()
    
    try:
        with open(file_path, mode='r') as csvfile:
            reader = csv.DictReader(csvfile)
            if not all(field in reader.fieldnames for field in ['RELEVE_ID', 'SPECIES_NAME', 'DOMIN']):
                raise ValueError("CSV file must contain RELEVE_ID, SPECIES_NAME, and DOMIN columns")
                
            for row in reader:
                releve_id = row['RELEVE_ID']
                species_name = row['SPECIES_NAME']
                domin_score = float(row['DOMIN'])
                
                # Update overall statistics
                species_scores[species_name] += domin_score
                unique_species.add(species_name)
                unique_releve_ids.add(releve_id)
                
                # Update per-RELEVE_ID statistics
                species_per_releve[releve_id].add(species_name)
                
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    if not species_scores:
        print("Error: No valid data found in the file.")
        sys.exit(1)
    
    max_species = max(species_scores.items(), key=lambda x: x[1])
    return species_scores, max_species, unique_species, species_per_releve, unique_releve_ids

def main():
    if len(sys.argv) != 2:
        print("Usage: python species_analysis.py <input_file.csv>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    results = analyze_species_data(file_path)
    species_scores, (top_species, top_score), unique_species, species_per_releve, unique_releve_ids = results
    
    # Print overall statistics
    print("\n=== Overall Species Analysis ===")
    print(f"Total number of unique surveys (RELEVE_ID): {len(unique_releve_ids)}")
    print(f"Total unique species across all surveys: {len(unique_species)}")
    print(f"Species with highest combined DOMIN score: {top_species} ({top_score:.1f})")
    
    # Print per-RELEVE_ID statistics
    print("\n=== Unique Species per Survey (RELEVE_ID) ===")
    for releve_id, species_set in sorted(species_per_releve.items()):
        print(f"RELEVE_ID {releve_id}: {len(species_set)} unique species")
    
    # Optional: Print detailed species list for each RELEVE_ID
    print("\n=== Detailed Species per Survey ===")
    for releve_id, species_set in sorted(species_per_releve.items()):
        print(f"\nRELEVE_ID {releve_id} ({len(species_set)} species):")
        for species in sorted(species_set):
            print(f"  - {species}")

if __name__ == "__main__":
    main()

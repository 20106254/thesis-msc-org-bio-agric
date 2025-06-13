import csv
import sys
from collections import defaultdict

def analyze_species_data(file_path):
    """Analyze species data and return comprehensive statistics."""
    species_scores = defaultdict(float)
    unique_species = set()
    species_per_site = defaultdict(set)
    
    try:
        with open(file_path, mode='r') as csvfile:
            reader = csv.DictReader(csvfile)
            if not all(field in reader.fieldnames for field in ['SITE_ID', 'SPECIES_NAME', 'DOMIN']):
                raise ValueError("CSV file must contain SITE_ID, SPECIES_NAME, and DOMIN columns")
                
            for row in reader:
                site_id = row['SITE_ID']
                species_name = row['SPECIES_NAME']
                try:
                    domin_score = float(row['DOMIN'])
                except ValueError:
                    continue  # skip rows with invalid DOMIN values
                
                # Update overall statistics
                species_scores[species_name] += domin_score
                unique_species.add(species_name)
                
                # Update per-SITE_ID statistics
                species_per_site[site_id].add(species_name)
                
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
    return species_scores, max_species, unique_species, species_per_site

def get_top_species(species_scores, n=50):
    """Return the top n species by their combined DOMIN scores."""
    sorted_species = sorted(species_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_species[:n]

def format_species_table(top_species):
    """Format the top species list as a readable table."""
    # Determine column widths
    max_name_len = max(len(name) for name, _ in top_species)
    rank_width = len(str(len(top_species))) + 2
    name_width = max(max_name_len, 12) + 2
    score_width = 10
    
    # Create header
    header = (f"{'Rank'.center(rank_width)} | {'Species Name'.ljust(name_width)} | {'DOMIN Score'.rjust(score_width)}")
    separator = "-" * (rank_width + name_width + score_width + 6)
    
    # Create rows
    rows = []
    for rank, (species, score) in enumerate(top_species, 1):
        rank_str = str(rank).rjust(rank_width)
        name_str = species.ljust(name_width)
        score_str = f"{score:.1f}".rjust(score_width)
        rows.append(f"{rank_str} | {name_str} | {score_str}")
    
    return "\n".join([header, separator] + rows)

def main():
    if len(sys.argv) != 2:
        print("Usage: python species_analysis.py <input_file.csv>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    results = analyze_species_data(file_path)
    species_scores, (top_species, top_score), unique_species, species_per_site = results
    
    # Print overall statistics
    print("\n=== Overall Species Analysis ===")
    print(f"Total unique species across all sites: {len(unique_species)}")
    print(f"Species with highest combined DOMIN score: {top_species} ({top_score:.1f})")
    
    # Print top 50 species in a formatted table
    top_50_species = get_top_species(species_scores, 50)
    print("\n=== Top 50 Species by DOMIN Score ===")
    print(format_species_table(top_50_species))
    
    # Print per-SITE_ID statistics
    print("\n=== Unique Species per Site (SITE_ID) ===")
    for site_id, species_set in sorted(species_per_site.items()):
        print(f"SITE_ID {site_id}: {len(species_set)} unique species")
    
    # Optional: Print detailed species list for each SITE_ID
    print("\n=== Detailed Species per Site ===")
    for site_id, species_set in sorted(species_per_site.items()):
        print(f"\nSITE_ID {site_id} ({len(species_set)} species):")
        for species in sorted(species_set):
            print(f"  - {species}")

if __name__ == "__main__":
    main()

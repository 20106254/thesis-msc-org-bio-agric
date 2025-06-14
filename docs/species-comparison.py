import pandas as pd
from io import StringIO
import requests

# URLs of the CSV files (using raw.githubusercontent.com for direct CSV access)
urls = {
    '2007': 'https://raw.githubusercontent.com/20106254/thesis-msc-org-bio-agric/github-pages/datasets/site-68-2007/2007-MID-RANGE.csv',
    '2022': 'https://raw.githubusercontent.com/20106254/thesis-msc-org-bio-agric/github-pages/datasets/site-68-2022/2022-DOMIN.csv',
    '2025': 'https://raw.githubusercontent.com/20106254/thesis-msc-org-bio-agric/github-pages/datasets/site-68-2025/COMBINED_MID_RANGE.csv'
}

# Dictionary to store species from each file
species_sets = {}

for year, url in urls.items():
    try:
        # Download the CSV file
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Read the CSV into a DataFrame
        df = pd.read_csv(StringIO(response.text))
        
        # Get unique species from the SPECIES_NAME column
        species_sets[year] = set(df['SPECIES_NAME'].str.strip().str.upper().dropna().unique())
        print(f"Found {len(species_sets[year])} unique species in {year} file")
        
    except Exception as e:
        print(f"\nError processing {year} file: {e}")
        print(f"URL used: {url}")
        continue

# Compare the species sets if we have at least 2 files
if len(species_sets) >= 2:
    # Find common species across all files
    common_species = set.intersection(*species_sets.values())
    print(f"\nCommon species across all files ({len(common_species)}):")
    for i, species in enumerate(sorted(common_species), 1):
        print(f"{i}. {species}")
    
    # Find species unique to each file
    for year, species in species_sets.items():
        other_years = [k for k in species_sets.keys() if k != year]
        other_species = set.union(*[species_sets[k] for k in other_years]) if other_years else set()
        
        unique_species = species - other_species
        print(f"\nSpecies unique to {year} file ({len(unique_species)}):")
        for i, sp in enumerate(sorted(unique_species), 1):
            print(f"{i}. {sp}")
        
    # Create a Venn diagram (optional - requires matplotlib-venn)
    try:
        from matplotlib_venn import venn3, venn3_circles
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(10, 8))
        venn3(species_sets.values(), set_labels=species_sets.keys())
        plt.title("Species comparison between datasets")
        plt.show()
        
    except ImportError:
        print("\nFor Venn diagram visualization, install matplotlib-venn: pip install matplotlib-venn")
else:
    print("\nNeed at least 2 files with species data to compare.")

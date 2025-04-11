import urllib.request
from io import StringIO
import re

def process_species_list(species_list):
    """
    Process a list of species names into the vegapp compatible format.
    Returns a string with the formatted output.
    """
    output = []
    
    output.append("SPECIES_LU_VERSION; ISGS Species List")
    output.append("TERMS_AND_CONDITIONS; Free to use, cite original source")
    
    output.append("SPECIES_NR;NAME;GENUS;SPECIES;AUTHOR;SYNONYM;VALID_NR;VALID_NAME;SECUNDUM")
    
    for i, species in enumerate(species_list, start=1):
        species = species.strip()
        if not species:
            continue
            
        if 'species' in species.lower() or 'sp.' in species.lower():
            genus = species.split()[0]
            name = f"{genus} sp."
            output.append(f"{i};{name};{genus};sp.;NA;FALSE;{i};{name};NA")
            continue
            
        if ' s. ' in species or ' var. ' in species or ' subsp. ' in species:
            parts = re.split(r'\s+(s\.|var\.|subsp\.)\s+', species)
            genus_species = parts[0]
            infraspecific = ' '.join(parts[1:])
            genus, species_epithet = genus_species.split()[:2]
            name = f"{genus} {species_epithet} {infraspecific}"
            output.append(f"{i};{name};{genus};{species_epithet} {infraspecific};NA;FALSE;{i};{name};NA")
            continue
            
        parts = species.split()
        if len(parts) >= 2:
            genus = parts[0]
            species_epithet = parts[1]
            name = f"{genus} {species_epithet}"
            output.append(f"{i};{name};{genus};{species_epithet};NA;FALSE;{i};{name};NA")
        else:
            genus = parts[0]
            name = f"{genus} sp."
            output.append(f"{i};{name};{genus};sp.;NA;FALSE;{i};{name};NA")
            
    return '\n'.join(output)

def read_species_from_url(url):
    """
    Read species list from a URL and return as a list of strings.
    """
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
            return [line.strip() for line in StringIO(data).readlines() if line.strip()]
    except Exception as e:
        print(f"Error reading from URL: {e}")
        return None

species_url = "https://raw.githubusercontent.com/20106254/thesis-msc-org-bio-agric/refs/heads/master/datasets/isgs/ISGS_species_list_uniq.txt"

species_list = read_species_from_url(species_url)

if species_list is None:
    print("Failed to read species list from URL. Exiting.")
    exit(1)

formatted_output = process_species_list(species_list)

print(formatted_output)

output_filename = "../datasets/vegapp/ISGS_vegapp_species_list.csv"
with open(output_filename, 'w', encoding='utf-8') as f:
    f.write(formatted_output)

print(f"\nSuccessfully processed {len(species_list)} species. Output saved to {output_filename}")

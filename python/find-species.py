target_species = {
    "Perennial ryegrass": "Lolium perenne",
    "Timothy": "Phleum pratense",
    "Meadow fescue": "Festuca pratensis",
    "White clover": "Trifolium repens",
    "Red clover": "Trifolium pratense",
    "Lucerne": "Medicago sativa",
    "Birdsfoot trefoil": "Lotus corniculatus",
    "Alsike clover": "Trifolium hybridum",
    "Sainfoin": "Onobrychis viciifolia",
    "Sheep's burnet": "Sanguisorba minor",
    "Yarrow": "Achillea millefolium",
    "Sheep's parsley": "Anthriscus sylvestris", 
    "Plantain": "Plantago lanceolata",  
    "Chicory": "Cichorium intybus"
}

input_file = "../datasets/isgs/ISGS_species_list_uniq.txt"  

found_species = {}
not_found = []

try:
    with open(input_file, 'r') as file:
        lines = [line.strip() for line in file.readlines()]  
    
    for common_name, latin_name in target_species.items():
        if latin_name in lines:
            found_species[common_name] = latin_name
        else:
            not_found.append(common_name)
    
    print("Found species:")
    for common_name, latin_name in found_species.items():
        print(f"- {common_name}: {latin_name}")
    
    print("\nNot found:")
    for name in not_found:
        print(f"- {name}")

except FileNotFoundError:
    print(f"Error: File '{input_file}' not found.")

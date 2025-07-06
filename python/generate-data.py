import pandas as pd
import random

random.seed(42) 

def generate_data_set(species_list):
    high_dominance_range = (8, 10)
    medium_dominance_range = (3, 7)
    low_dominance_range = (1, 4)
    data_set = []

    for i in range(0, 20):
        no_of_species = random.randint(1, 3)
        selected_species = random.sample(species_list, no_of_species)
        
        for species in selected_species:
            data_set.append({
                'RELEVE_ID': i + 1,
                'SPECIES_NAME': species,  
                'DOMIN': random.randint(*high_dominance_range),
                'RICHNESS_GROUP': 'low'
            })

    for j in range(20, 40):
        no_of_species = random.randint(8, 12)
        selected_species = random.sample(species_list, no_of_species)
        
        for species in selected_species:
            data_set.append({
                'RELEVE_ID': j + 1,
                'SPECIES_NAME': species,
                'DOMIN': random.randint(*medium_dominance_range),
                'RICHNESS_GROUP': 'medium'
            })

    for k in range(40, 60):
        no_of_species = random.randint(18, 25)
        selected_species = random.sample(species_list, no_of_species)
        
        for species in selected_species:
            data_set.append({
                'RELEVE_ID': k + 1,
                'SPECIES_NAME': species,
                'DOMIN': random.randint(*low_dominance_range),
                'RICHNESS_GROUP': 'high'
            })

    return data_set

def get_species_list(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def write_data_set(data):
    df = pd.DataFrame(data)
    print("Dataset summary:")
    print(f"Total records: {len(df)}")
    print(f"Unique RELEVE_IDs: {df['RELEVE_ID'].nunique()}")
    print(f"Species richness by group:\n{df.groupby('RICHNESS_GROUP')['RELEVE_ID'].nunique()}")
    df.to_csv("../datasets/generated-data/generated-data-set.csv", index=False)

if __name__ == "__main__":
    species_list = get_species_list("../datasets/generated-data/2007-species.txt")
    generated_data = generate_data_set(species_list)
    write_data_set(generated_data)

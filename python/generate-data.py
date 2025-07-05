import pandas as pd
import numpy as np
import random

def generate_data_set(species_list):
    no_of_species = 0
    high_dominance_range = (8, 10)
    medium_dominance_range = (3, 7)  
    low_dominance_range = (1, 4)
    data_set = []

    for i in range(0, 20):
        no_of_species = random.randint(1, 3)
        selected_species = random.sample(species_list, no_of_species)

        for species in selected_species:
            dominance_score = random.randint(*high_dominance_range)
            data_set.append({
                'RELEVE_ID': i + 1,
                'SPECIES_NAME': f"'{species}'",
                'DOMIN': dominance_score
            })


    for j in range(20, 40):
        no_of_species = random.randint(8, 12)
        selected_species = random.sample(species_list, no_of_species)

        for species in selected_species:
            dominance_score = random.randint(*medium_dominance_range)
            data_set.append({
                'RELEVE_ID': j + 1,
                'SPECIES_NAME': f"'{species}'",
                'DOMIN': dominance_score
            })           

    for k in range(40, 60):
        no_of_species = random.randint(18, 25)
        print(f"Number of species: {no_of_species}")
        selected_species = random.sample(species_list, no_of_species)
        print(f"High richness group - RELEVE_ID {k+1}: {len(selected_species)} species selected")

        for species in selected_species:
            dominance_score = random.randint(*low_dominance_range)
            data_set.append({
                'RELEVE_ID': k + 1,
                'SPECIES_NAME': f"'{species}'",
                'DOMIN': dominance_score
            })            

    return data_set
            

def get_species_list(file_path):
    with open(file_path, 'r') as file:
        species = [line.strip() for line in file if line.strip()]
    return species

def write_data_set(data):
    releve_df = pd.DataFrame(data)
    print(releve_df.head())
    releve_df.to_csv("../datasets/generated-data/generated-data-set.csv", index=False)


species_file_path = "../datasets/generated-data/2007-species.txt"
species_list = get_species_list(species_file_path)
generated_data = generate_data_set(species_list)
write_data_set(generated_data)


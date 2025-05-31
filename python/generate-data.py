import pandas as pd
import numpy as np
import random

def generate_data_set(species_list, grass_species):
    no_of_species = 0
    # Updated ranges with discrete values
    high_dominance_values = [18, 30, 42, 63, 83, 96]
    dominance_values = [0.1, 0.3, 0.5, 3, 8, 18, 30, 42, 63, 83, 96]
    data_set = []

    for i in range(1, 20):
        no_of_species = random.randint(10, 12)
        selected_species = random.sample(grass_species, no_of_species)

        for species in selected_species:
            # Choose from full dominance range for grasses
            dominance_score = random.choice(dominance_values)
            data_set.append({
                'RELEVE_ID': i,
                'SPECIES_NAME': f"'{species}'",
                'DOMIN': dominance_score
            })

    for j in range(21, 60):
        no_of_species = random.randint(20, 30)
        selected_species = random.sample(species_list, no_of_species)

        for species in selected_species:
            # 30% chance to get high dominance value, otherwise regular dominance
            if random.random() < 0.3:
                dominance_score = random.choice(high_dominance_values)
            else:
                dominance_score = random.choice(dominance_values)
            data_set.append({
                'RELEVE_ID': j,
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
    releve_df.to_csv("generated-data-set.csv", index=False)

species_file_path = "../datasets/site-68-2007/2007-survey.txt"
grass_species_file_path = "../datasets/site-68-2007/2007-survey-grasses.txt"
species_list = get_species_list(species_file_path)
grasses_list = get_species_list(grass_species_file_path)
generated_data = generate_data_set(species_list, grasses_list)
write_data_set(generated_data)

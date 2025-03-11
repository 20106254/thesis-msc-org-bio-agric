import pandas as pd
import numpy as np
import random

def generate_data_set(species_list):
    no_of_species = 0
    releves = 50
    low = 10
    medium = 20
    dominance_range = (1, 10)
    data_set = []

    for i in range(releves):

        if i < low:
            no_of_species = random.randint(5, 10)
        elif i < medium:
            no_of_species = random.randint(11, 20)
        else:
            no_of_species = random.randint(21, 50)

        selected_species = random.sample(species_list, no_of_species)

        for species in selected_species:
            dominance_score = random.randint(*dominance_range)
            data_set.append({
                'RELEVE_ID': i + 1,
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


species_file_path = "../datasets/2007-survey.txt"
species_list = get_species_list(species_file_path)
generated_data = generate_data_set(species_list)
write_data_set(generated_data)



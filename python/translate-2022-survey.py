import csv

dataset = '../datasets/site-68-2022/Site-0068.csv'

def translate_score(score):
    if score >= 75:
        return 5
    elif score >= 50:
        return 4
    elif score >= 25:
        return 3
    elif score >= 5:
        return 2
    elif score >= 1:
        return 1
    elif score >= 0.5:
        return 0.5
    elif score >= 0.1:
        return 0.1
    else:
        return 0

processed_data = {30: {}, 31: {}, 32: {}, 33: {}, 34: {}}

with open(dataset, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        species_name = row[0].strip()
        for i, score in enumerate(row[1:]):
            if score:  # Only process non-empty scores
                releve_id = 30 + i
                braun_blanquet_value = translate_score(float(score))
                if braun_blanquet_value != 0:
                    processed_data[releve_id][species_name] = braun_blanquet_value

# Write processed data to a new CSV file
with open('translated_data.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['RELEVE_ID', 'SPECIES_NAME', 'DOMIN'])
    for releve_id in processed_data:
        for species_name, braun_blanquet_value in processed_data[releve_id].items():
            csvwriter.writerow([releve_id, species_name, braun_blanquet_value])

print("Data has been translated and written to translated_data.csv")

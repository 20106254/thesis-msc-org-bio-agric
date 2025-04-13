import pandas as pd

def convert_dominance_values(input_file, output_file):
    dominance_mapping = {
        0.1: 0.1,  
        1: ,
        2: 2,
        3: 3,
        4: 4,
        5: 5,
        6: 6,
        7: 7,
        8: 8,
        9: 9,
        10: 10
    }
    
    df = pd.read_csv(input_file)
    
    df['DOMIN'] = df['DOMIN'].apply(lambda x: dominance_mapping.get(x, x))
    
    df.to_csv(output_file, index=False)
    print(f"File converted and saved to {output_file}")

input_file = "../datasets/isgs/RELEVE_SP_DATA_V2.txt"  
output_file = "../datasets/isgs/RELEVE_SP_DATA_MID_RANGE.txt"  
convert_dominance_values(input_file, output_file)

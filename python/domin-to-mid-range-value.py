import pandas as pd
import argparse

def convert_dominance_values(input_file, output_file):
    """
    Convert DOMIN values to their mid-range equivalents and save to a new CSV file.
    
    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path to save the converted CSV file
    """
    dominance_mapping = {
        0.1: 0.1,
        1: 0.3,
        2: 0.5,
        3: 3,
        4: 8,
        5: 18,
        6: 30,
        7: 42,
        8: 63,
        9: 83,
        10: 96
    }

    df = pd.read_csv(input_file)
    df['DOMIN'] = df['DOMIN'].apply(lambda x: dominance_mapping.get(x, x))
    df.to_csv(output_file, index=False)
    print(f"File converted and saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert DOMIN values to mid-range equivalents')
    parser.add_argument('input_file', help='Path to input CSV file')
    parser.add_argument('output_file', help='Path to output CSV file')
    
    args = parser.parse_args()
    
    convert_dominance_values(args.input_file, args.output_file)

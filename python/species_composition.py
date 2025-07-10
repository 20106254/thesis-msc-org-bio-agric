import pandas as pd
import matplotlib.pyplot as plt
import argparse
import sys

def create_dominance_chart(csv_path, output_svg="dominant_species.svg", top_n=5):
    """Create a compact dominance pie chart from CSV data"""
    try:
        # Read and process data
        df = pd.read_csv(csv_path)
        species_totals = df.groupby("SPECIES_NAME")["DOMIN"].sum().reset_index()
        top_species = species_totals.sort_values("DOMIN", ascending=False).head(top_n)
        
        # Setup compact figure
        plt.figure(figsize=(4, 3))
        plt.rcParams['font.size'] = 7
        
        # Create pie chart
        colors = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f'][:top_n]
        wedges, _ = plt.pie(
            top_species["DOMIN"],
            colors=colors,
            wedgeprops={"linewidth": 0.5, "edgecolor": "white"},
            startangle=90
        )
        
        # Add minimal legend
        legend_labels = [f"{row['SPECIES_NAME']} ({row['DOMIN']:.1f})" 
                       for _, row in top_species.iterrows()]
        plt.legend(wedges, legend_labels,
                  title=f"Top {top_n} Species",
                  loc="center left",
                  bbox_to_anchor=(1, 0.5),
                  fontsize=6,
                  frameon=False)
        
        plt.title(f"Dominant Species (Top {top_n})", fontsize=8, pad=5)
        plt.tight_layout(pad=1)
        plt.savefig(output_svg, format="svg", bbox_inches="tight")
        plt.close()
        
        print(f"Successfully created {output_svg}")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create dominant species pie chart')
    parser.add_argument('csv_file', help='Path to input CSV file')
    parser.add_argument('-o', '--output', default="dominant_species.svg", 
                       help='Output SVG filename')
    parser.add_argument('-n', '--top_n', type=int, default=5,
                       help='Number of top species to display')
    
    args = parser.parse_args()
    
    if not create_dominance_chart(args.csv_file, args.output, args.top_n):
        sys.exit(1)

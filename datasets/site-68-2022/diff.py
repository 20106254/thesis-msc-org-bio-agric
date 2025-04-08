#!/usr/bin/env python3
import sys

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def load_species(filename):
    """Load species while preserving original formatting"""
    try:
        with open(filename, 'r') as f:
            # Store original lines but use normalized version for comparison
            return {
                line.strip().casefold(): line.strip() 
                for line in f 
                if line.strip()
            }
    except FileNotFoundError:
        print(f"{Colors.RED}Error:{Colors.END} File '{filename}' not found")
        sys.exit(1)

def compare_files(file1, file2):
    """Compare files while preserving original formatting in output"""
    species1 = load_species(file1)
    species2 = load_species(file2)

    # Get normalized keys
    norm1 = set(species1.keys())
    norm2 = set(species2.keys())

    # Find differences using normalized names
    unique_to_file1 = norm1 - norm2
    unique_to_file2 = norm2 - norm1
    common = norm1 & norm2

    # Print results with original formatting
    def print_section(color, title, items, source_dict):
        print(f"\n{color}{Colors.BOLD}{title}:{Colors.END} {len(items)} species")
        # Get original formatting from source dictionary
        original_items = [source_dict[item] for item in sorted(items)]
        print('\n'.join(original_items) if items else "None")

    print_section(Colors.RED, f"Unique to {file1}", unique_to_file1, species1)
    print_section(Colors.GREEN, f"Unique to {file2}", unique_to_file2, species2)
    
    # For common species, prefer file1's formatting
    common_original = [species1.get(item, species2[item]) for item in sorted(common)]
    print(f"\n{Colors.BLUE}{Colors.BOLD}Common species:{Colors.END} {len(common)}")
    print('\n'.join(common_original) if common else "None")

    # Calculate similarity
    total_species = len(norm1 | norm2)
    similarity = len(common) / total_species * 100 if total_species > 0 else 0
    print(f"\n{Colors.BOLD}Comparison summary:{Colors.END}")
    print(f"• Total unique species: {len(unique_to_file1) + len(unique_to_file2)}")
    print(f"• Shared species: {len(common)}")
    print(f"• Similarity: {similarity:.1f}%")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"{Colors.BOLD}Usage:{Colors.END} {sys.argv[0]} <file1> <file2>")
        sys.exit(1)
    
    compare_files(sys.argv[1], sys.argv[2])

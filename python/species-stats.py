import csv
import sys
import json
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import shutil
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader

def analyze_species_data(file_path):
    """Analyze species data and return comprehensive statistics."""
    species_data = defaultdict(list)
    species_scores = defaultdict(float)
    unique_species = set()
    species_per_releve = defaultdict(set)
    unique_releve_ids = set()
    total_domin_score = 0.0
    
    try:
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            if not all(field in reader.fieldnames for field in ['RELEVE_ID', 'SPECIES_NAME', 'DOMIN']):
                raise ValueError("CSV file must contain RELEVE_ID, SPECIES_NAME, and DOMIN columns")
                
            for row in reader:
                releve_id = int(row['RELEVE_ID'])
                species_name = row['SPECIES_NAME']
                domin_score = float(row['DOMIN'])
                
                species_data[releve_id].append({
                    'name': species_name,
                    'score': domin_score
                })
                
                species_scores[species_name] += domin_score
                unique_species.add(species_name)
                unique_releve_ids.add(releve_id)
                total_domin_score += domin_score
                species_per_releve[releve_id].add(species_name)
                
    except Exception as e:
        print(f"Error analyzing data: {str(e)}")
        raise
    
    if not species_scores:
        raise ValueError("No valid data found in the file")
    
    # Classify by management type
    management_data = {
        'Grazing+Fertiliser': {'releves': [], 'species': defaultdict(float)},
        'Mowing+Fertiliser': {'releves': [], 'species': defaultdict(float)},
        'Organic': {'releves': [], 'species': defaultdict(float)}
    }
    
    for releve_id, records in species_data.items():
        if 1 <= releve_id <= 10:
            mgmt = 'Grazing+Fertiliser'
        elif 28 <= releve_id <= 38:
            mgmt = 'Mowing+Fertiliser'
        else:
            mgmt = 'Organic'
            
        management_data[mgmt]['releves'].append(releve_id)
        for r in records:
            management_data[mgmt]['species'][r['name']] += r['score']
    
    # Calculate management-level stats
    management_stats = {}
    for mgmt, data in management_data.items():
        total_score = sum(data['species'].values())
        if total_score > 0:
            top_species = max(data['species'].items(), key=lambda x: x[1])
            management_stats[mgmt] = {
                'releve_count': len(data['releves']),
                'total_score': total_score,
                'top_species': top_species[0],
                'top_score': top_species[1],
                'species_proportions': data['species']
            }
    
    return {
        'management_stats': management_stats,
        'unique_species': unique_species,
        'unique_releve_ids': unique_releve_ids,
        'total_domin_score': total_domin_score,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def run_r_nmds_analysis(csv_path, output_dir):
    """Run external R script to perform NMDS analysis."""
    try:
        r_script_path = Path("../R-code/nmds.R")
        if not r_script_path.exists():
            raise FileNotFoundError(f"R script not found at {r_script_path}")
        
        # Create output directory for R results
        r_output_dir = Path(output_dir) / "r_output"
        r_output_dir.mkdir(exist_ok=True)
        
        # Execute R script
        result = subprocess.run(
            ["Rscript", str(r_script_path), csv_path, str(r_output_dir)],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Load R output metrics
        metrics_file = r_output_dir / "nmds_metrics.json"
        if not metrics_file.exists():
            raise FileNotFoundError("R script did not generate metrics file")
        
        with open(metrics_file, 'r') as f:
            metrics = json.load(f)
        
        return {
            'success': True,
            'metrics': metrics,
            'svg_path': r_output_dir / "nmds_plot.svg"
        }
        
    except subprocess.CalledProcessError as e:
        return {
            'success': False,
            'error': f"R script failed: {e.stderr}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def generate_html_report(results, input_filename, output_dir="../docs", template_file="../templates/report_template.html"):
    try:
        # Set up paths
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        input_path = Path(input_filename)
        output_file = output_path / f"{input_path.stem}_report.html"
        template_path = Path(template_file)
        
        # Run NMDS analysis
        nmds_result = run_r_nmds_analysis(input_filename, output_dir)
        if not nmds_result['success']:
            raise RuntimeError(f"NMDS analysis failed: {nmds_result.get('error', 'Unknown error')}")
        
        # Copy SVG to report directory
        nmds_svg = output_path / "nmds_plot.svg"
        nmds_svg_exists = False
        if nmds_result.get('svg_path'):
            shutil.copy(nmds_result['svg_path'], nmds_svg)
            nmds_svg_exists = True

        # Find overall top species
        all_species = {}
        for mgmt, stats in results['management_stats'].items():
            for species, score in stats['species_proportions'].items():
                all_species[species] = all_species.get(species, 0) + score

        top_species, top_score = (max(all_species.items(), key=lambda x: x[1]) if all_species else ("N/A", 0))

        # Prepare management types for template
        management_types = {
            'Grazing+Fertiliser': results['management_stats'].get('Grazing+Fertiliser', {}),
            'Mowing+Fertiliser': results['management_stats'].get('Mowing+Fertiliser', {}),
            'Organic': results['management_stats'].get('Organic', {})
        }

        # Set up Jinja2 environment
        env = Environment(loader=FileSystemLoader(str(template_path.parent)))
        template = env.get_template(template_path.name)

        # Prepare context data
        context = {
            'timestamp': results['timestamp'],
            'total_releves': len(results['unique_releve_ids']),
            'unique_species_count': len(results['unique_species']),
            'top_species': top_species,
            'top_score': top_score,
            'nmds_stress': float(nmds_result['metrics'].get('stress_value', 0)),
            'nmds_metrics': nmds_result['metrics'],
            'management_stats': management_types,
            'nmds_svg_exists': nmds_svg_exists,
            'input_filename': input_path.name
        }

        # Render and save template
        html_output = template.render(context)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_output)

        print(f"Report generated: {output_file}")
        return str(output_file)
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        raise       

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python species_analysis.py <input_file.csv>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    try:
        input_path = Path(input_file)
        if not input_path.exists():
            print(f"Error: Input file '{input_file}' not found")
            sys.exit(1)
            
        results = analyze_species_data(input_file)
        output_file = generate_html_report(results, input_file)
        
        if output_file:
            print(f"Open file://{Path(output_file).absolute()} in your browser")
        else:
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

import csv
import sys
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

def analyze_species_data(file_path):
    """Analyze species data and return comprehensive statistics."""
    species_data = defaultdict(list)  # Store raw records per relevé
    species_scores = defaultdict(float)  # For overall species totals
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
                releve_id = row['RELEVE_ID']
                species_name = row['SPECIES_NAME']
                domin_score = float(row['DOMIN'])
                
                # Store raw records for each relevé
                species_data[releve_id].append({
                    'name': species_name,
                    'score': domin_score
                })
                
                # Update overall statistics
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
    
    # Calculate max DOMIN and proportions PER RELEVÉ
    releve_stats = {}
    for releve_id, records in species_data.items():
        total_releve_score = sum(r['score'] for r in records)
        max_record = max(records, key=lambda x: x['score'])
        
        releve_stats[releve_id] = {
            'species_proportions': {r['name']: r['score'] for r in records},
            'max_domin': max_record['score'],
            'max_species': max_record['name'],
            'total_releve_score': total_releve_score
        }
    
    max_species = max(species_scores.items(), key=lambda x: x[1])
    avg_domin_per_species = total_domin_score / len(unique_species) if unique_species else 0
    
    return {
        'releve_stats': releve_stats,
        'species_scores': species_scores,
        'top_species': max_species[0],
        'top_score': max_species[1],
        'unique_species': unique_species,
        'species_per_releve': species_per_releve,
        'unique_releve_ids': unique_releve_ids,
        'total_domin_score': total_domin_score,
        'avg_domin_per_species': avg_domin_per_species,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def generate_html_report(results, input_filename, output_dir="../docs"):
    """Generate an HTML report with accurate pie charts for each relevé."""
    try:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        input_path = Path(input_filename)
        output_file = output_path / f"{input_path.stem}_report.html"

        # Prepare survey data using per-relevé statistics
        survey_data = []
        for releve_id, stats in results['releve_stats'].items():
            survey_data.append({
                'id': int(releve_id),
                'count': len(stats['species_proportions']),
                'species_data': stats['species_proportions'],
                'max_domin': stats['max_domin'],
                'max_species': stats['max_species'],
                'total_score': stats['total_releve_score']
            })
        
        # Numeric sort by Relevé ID
        survey_data.sort(key=lambda x: x['id'])
        
        # Generate table rows with pie charts
        table_rows = []
        for item in survey_data:
            # Sort species by dominance and convert to JSON
            sorted_species = sorted(
                item['species_data'].items(),
                key=lambda x: -x[1]
            )
            species_json = json.dumps([
                {'species': k, 'score': v} 
                for k,v in sorted_species
            ])
            
            table_rows.append(
                f"<tr>"
                f"<td>{item['id']}</td>"
                f"<td>{item['count']}</td>"
                f"<td class='domin-score'>{item['max_domin']:.1f} ({item['max_species']})</td>"
                f"<td><div id='pie-{item['id']}' class='pie-container'></div></td>"
                f"<script>"
                f"Plotly.newPlot('pie-{item['id']}', [{{"
                f"values: {species_json}.map(x => x.score),"
                f"labels: {species_json}.map(x => x.species),"
                f"type: 'pie',"
                f"textinfo: 'percent',"
                f"hoverinfo: 'label+percent+value',"
                f"}}], {{margin: {{t:0, b:0, l:0, r:0}}, showlegend: false}});"
                f"</script>"
                f"</tr>"
            )
        table_rows_html = "".join(table_rows)
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Species Analysis Report</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        h1 {{
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        .summary-cards {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            padding: 20px;
            flex: 1;
            min-width: 200px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .domin-score {{
            font-weight: bold;
            color: #e53935;
        }}
        .pie-container {{
            width: 300px;
            height: 200px;
        }}
    </style>
</head>
<body>
    <h1>Species Analysis Report</h1>
    <p>Generated on: {results['timestamp']}</p>
    
    <div class="summary-cards">
        <div class="card">
            <h3>Total Relevés</h3>
            <div class="card-value">{len(results['unique_releve_ids'])}</div>
        </div>
        <div class="card">
            <h3>Unique Species</h3>
            <div class="card-value">{len(results['unique_species'])}</div>
        </div>
        <div class="card">
            <h3>Highest DOMIN Overall</h3>
            <div class="card-value">{results['top_species']}</div>
            <div class="domin-score">Score: {results['top_score']:.1f}</div>
        </div>
    </div>
    
    <h2>Relevé Summary</h2>
    <table>
        <thead>
            <tr>
                <th>Relevé ID</th>
                <th>Species Count</th>
                <th>Max DOMIN Score</th>
                <th>Species Composition</th>
            </tr>
        </thead>
        <tbody>
            {table_rows_html}
        </tbody>
    </table>
</body>
</html>"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Successfully generated report: {output_file}")
        return str(output_file)
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return None

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
            print("Report generation completed successfully!")
            print(f"Open file://{Path(output_file).absolute()} in your browser")
        else:
            print("Report generation failed")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

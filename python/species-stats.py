import csv
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

def analyze_species_data(file_path):
    """Analyze species data and return comprehensive statistics."""
    species_data = defaultdict(list)
    species_scores = defaultdict(float)
    unique_species = set()
    species_per_releve = defaultdict(set)
    unique_releve_ids = set()
    total_domin_score = 0.0
    
    try:
        with open(file_path, mode='r') as csvfile:
            reader = csv.DictReader(csvfile)
            if not all(field in reader.fieldnames for field in ['RELEVE_ID', 'SPECIES_NAME', 'DOMIN']):
                raise ValueError("CSV file must contain RELEVE_ID, SPECIES_NAME, and DOMIN columns")
                
            for row in reader:
                releve_id = row['RELEVE_ID']
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
    
    max_per_survey = {}
    for releve_id, records in species_data.items():
        max_record = max(records, key=lambda x: x['score'])
        max_per_survey[releve_id] = {
            'species': max_record['name'],
            'score': max_record['score']
        }
    
    max_species = max(species_scores.items(), key=lambda x: x[1])
    avg_domin_per_species = total_domin_score / len(unique_species) if unique_species else 0
    
    return {
        'species_scores': species_scores,
        'top_species': max_species[0],
        'top_score': max_species[1],
        'unique_species': unique_species,
        'species_per_releve': species_per_releve,
        'unique_releve_ids': unique_releve_ids,
        'total_domin_score': total_domin_score,
        'avg_domin_per_species': avg_domin_per_species,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'max_per_survey': max_per_survey
    }

def generate_html_report(results, input_filename, output_dir="../docs"):
    """Generate an HTML report in the specified docs directory."""
    try:
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create output filename
        input_path = Path(input_filename)
        output_file = output_path / f"{input_path.stem}_report.html"

        survey_data = []
        for releve_id, species_set in results['species_per_releve'].items():
            max_info = results['max_per_survey'][releve_id]
            survey_data.append({
                'id': int(releve_id),  # Convert to integer for sorting
                'count': len(species_set),
                'species': ', '.join(sorted(species_set)),
                'max_domin': max_info['score'],
                'max_species': max_info['species']
            })
        
        # Numeric sort by Survey ID
        survey_data.sort(key=lambda x: x['id'])
        
        # Convert back to strings for display
        for item in survey_data:
            item['id'] = str(item['id'])
        
        table_rows = []
        for item in survey_data:
            table_rows.append(
                f"<tr>"
                f"<td>{item['id']}</td>"
                f"<td>{item['count']}</td>"
                f"<td class='domin-score'>{item['max_domin']:.1f} ({item['max_species']})</td>"
                f"<td>{item['species']}</td>"
                f"</tr>"
            )
        table_rows_html = "".join(table_rows)
       
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Species Analysis Report</title>
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
        .highlight-card {{
            background: #e3f2fd;
            border-left: 4px solid #3498db;
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
            cursor: pointer;
            position: relative;
        }}
        th:hover {{
            background-color: #2980b9;
        }}
        th.sort-asc::after {{
            content: " ↑";
            font-weight: bold;
        }}
        th.sort-desc::after {{
            content: " ↓";
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .domin-score {{
            font-weight: bold;
            color: #e53935;
        }}
    </style>
</head>
<body>
    <h1>Species Analysis Report</h1>
    <p>Generated on: {results['timestamp']}</p>
    
    <div class="summary-cards">
        <div class="card">
            <h3>Total Surveys</h3>
            <div class="card-value">{len(results['unique_releve_ids'])}</div>
        </div>
        <div class="card">
            <h3>Unique Species</h3>
            <div class="card-value">{len(results['unique_species'])}</div>
        </div>
        <div class="card highlight-card">
            <h3>Highest DOMIN Overall</h3>
            <div class="card-value">{results['top_species']}</div>
            <div class="domin-score">Score: {results['top_score']:.1f}</div>
        </div>
    </div>
    
    <h2>Survey Summary</h2>
    <table id="surveyTable">
        <thead>
            <tr>
                <th onclick="sortTable(0)">Survey ID</th>
                <th onclick="sortTable(1, true)">Unique Species Count</th>
                <th onclick="sortTable(2, true)">Max DOMIN Score</th>
                <th>Species List</th>
            </tr>
        </thead>
        <tbody>
            {table_rows_html}
        </tbody>
    </table>

    <script>
        let currentSortColumn = null;
        let isAscending = true;
        
        function sortTable(column, isNumeric = false) {{
            const table = document.getElementById("surveyTable");
            const tbody = table.querySelector("tbody");
            const rows = Array.from(tbody.querySelectorAll("tr"));
            const headers = table.querySelectorAll("th");
            
            headers.forEach(header => {{
                header.classList.remove("sort-asc", "sort-desc");
            }});
            
            if (currentSortColumn === column) {{
                isAscending = !isAscending;
            }} else {{
                currentSortColumn = column;
                isAscending = true;
            }}
            
            rows.sort((a, b) => {{
                let aVal = a.cells[column].textContent.trim();
                let bVal = b.cells[column].textContent.trim();
                
                if (column === 0) {{
                    // Special handling for Survey ID
                    aVal = parseInt(aVal);
                    bVal = parseInt(bVal);
                    return isAscending ? aVal - bVal : bVal - aVal;
                }}
                else if (column === 1 || column === 2) {{
                    // For counts and DOMIN scores
                    if (column === 2) {{
                        aVal = parseFloat(aVal.split(' ')[0]);
                        bVal = parseFloat(bVal.split(' ')[0]);
                    }} else {{
                        aVal = parseInt(aVal);
                        bVal = parseInt(bVal);
                    }}
                    return isAscending ? aVal - bVal : bVal - aVal;
                }}
                
                return isAscending 
                    ? aVal.localeCompare(bVal) 
                    : bVal.localeCompare(aVal);
            }});
            
            rows.forEach(row => tbody.appendChild(row));
            headers[column].classList.add(isAscending ? "sort-asc" : "sort-desc");
        }}
        
        // Initial sort by Max DOMIN score (descending)
        document.addEventListener('DOMContentLoaded', function() {{
            sortTable(2, true);
        }});
    </script>
</body>
</html>"""       
        
        with open(output_file, 'w') as f:
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
            print(f"GitHub Pages URL: https://<your-username>.github.io/<repo-name>/docs/{input_path.stem}_report.html")
        else:
            print("Report generation failed")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

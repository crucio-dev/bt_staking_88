#!/usr/bin/env python3
"""
How to use:
python score_to_json.py output.log > table_data.json

"""

import json
import sys
import re

def simple_extract_table(text):
    """Simple extraction using regex pattern matching"""
    
    # Find the table pattern
    # Look for lines that start with uid header and data rows
    lines = text.strip().split('\n')
    
    table_lines = []
    capturing = False
    
    for line in lines:
        # Start capturing when we see the header
        if 'uid' in line and 'date' in line and 'days' in line:
            table_lines.append(line.strip())
            capturing = True
        elif capturing and line.strip():
            # Continue capturing data lines (lines that start with numbers)
            if re.match(r'^\s*\d+', line):
                table_lines.append(line.strip())
            elif not line.strip():
                continue  # Skip empty lines
            else:
                break  # Stop when we hit non-data content
    
    if len(table_lines) < 2:
        return {"error": "Incomplete table found"}
    
    # Parse the table
    headers = table_lines[0].split()
    data = []
    
    for line in table_lines[1:]:
        fields = line.split()
        if len(fields) >= len(headers):
            row = {}
            for i, header in enumerate(headers):
                if i < len(fields):
                    value = fields[i]
                    
                    # Simple type conversion
                    if header in ['uid', 'days']:
                        row[header] = int(value)
                    elif header == 'date':
                        row[header] = value
                    elif value.endswith('%'):
                        row[header] = float(value.replace('%', ''))
                    elif '.' in value and value.replace('.', '').replace('-', '').isdigit():
                        row[header] = float(value)
                    elif value.isdigit():
                        row[header] = int(value)
                    else:
                        row[header] = value
            data.append(row)
    
    return {"data": data, "count": len(data)}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            content = f.read()
    else:
        content = sys.stdin.read()
    
    result = simple_extract_table(content)
    print(json.dumps(result, indent=2))

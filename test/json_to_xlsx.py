#!/usr/bin/env python3
"""
How to Run:
python json_to_xlsx.py results.json staking_analysis.xlsx
"""

import json
import sys
import pandas as pd
from datetime import datetime
import os

def json_to_xlsx(json_data, output_file=None):
    """Convert JSON data to Excel file"""
    
    try:
        # Parse JSON if it's a string
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        
        # Extract the data array
        if 'data' in data:
            records = data['data']
        elif isinstance(data, list):
            records = data
        else:
            raise ValueError("JSON must contain 'data' array or be an array itself")
        
        if not records:
            raise ValueError("No data records found")
        
        # Create DataFrame
        df = pd.DataFrame(records)
        
        # Generate output filename if not provided
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"staking_results_{timestamp}.xlsx"
        
        # Ensure .xlsx extension
        if not output_file.endswith('.xlsx'):
            output_file += '.xlsx'
        
        # Write to Excel with formatting
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Staking Results', index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Staking Results']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Format percentage columns
            from openpyxl.styles import NamedStyle
            
            percent_style = NamedStyle(name="percent_style")
            percent_style.number_format = '0.00%'
            
            # Apply percentage formatting to percentage columns
            percent_columns = ['apy%', 'risk%', 'odds%', 'daily%', 'yield%']
            
            for col_idx, col_name in enumerate(df.columns, 1):
                if col_name in percent_columns:
                    col_letter = worksheet.cell(row=1, column=col_idx).column_letter
                    for row in range(2, len(df) + 2):  # Skip header row
                        cell = worksheet[f"{col_letter}{row}"]
                        # Convert percentage values (divide by 100 since they're already in percentage form)
                        if cell.value is not None:
                            cell.value = cell.value / 100
                        cell.number_format = '0.00%'
        
        return {
            "success": True,
            "output_file": output_file,
            "records_count": len(records),
            "columns": list(df.columns),
            "file_size": os.path.getsize(output_file) if os.path.exists(output_file) else 0
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: python json_to_xlsx.py <json_file> [output_file.xlsx]")
        print("   or: cat data.json | python json_to_xlsx.py - [output_file.xlsx]")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        # Read JSON data
        if json_file == '-':
            # Read from stdin
            json_content = sys.stdin.read()
        else:
            # Read from file
            with open(json_file, 'r') as f:
                json_content = f.read()
        
        # Convert to Excel
        result = json_to_xlsx(json_content, output_file)
        
        if result['success']:
            print(f"✅ Successfully converted to Excel!")
            print(f"📁 Output file: {result['output_file']}")
            print(f"📊 Records: {result['records_count']}")
            print(f"📋 Columns: {', '.join(result['columns'])}")
            print(f"💾 File size: {result['file_size']} bytes")
        else:
            print(f"❌ Error: {result['error']}")
            sys.exit(1)
            
    except FileNotFoundError:
        print(f"❌ Error: File '{json_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

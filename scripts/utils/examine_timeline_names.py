#!/usr/bin/env python3
"""
Script to examine the timeline_names.xlsx file structure
"""

import pandas as pd
import sys
from pathlib import Path

def examine_excel_file():
    """Examine the structure of the timeline_names.xlsx file"""
    
    excel_path = Path("content/timeline_names.xlsx")
    
    if not excel_path.exists():
        print(f"Error: Excel file not found at {excel_path}")
        return
    
    try:
        # Read the Excel file
        print("Reading Excel file...")
        xl_file = pd.ExcelFile(excel_path)
        
        # Show all sheet names
        print(f"Available sheets: {xl_file.sheet_names}")
        
        # Read the "names" sheet specifically
        if "names" in xl_file.sheet_names:
            print("\n--- 'names' sheet content ---")
            df = pd.read_excel(excel_path, sheet_name="names")
            
            print(f"Columns: {list(df.columns)}")
            print(f"Number of rows: {len(df)}")
            
            # Show first few rows
            print("\nFirst 10 rows:")
            print(df.head(10).to_string())
            
            # Check if the expected columns exist
            if 'timeline' in df.columns and 'description' in df.columns:
                print(f"\n✓ Found both 'timeline' and 'description' columns")
                
                # Show some examples
                print("\nSample timeline-description pairs:")
                for i, row in df.head(5).iterrows():
                    timeline = row.get('timeline', 'N/A')
                    description = row.get('description', 'N/A')
                    print(f"  {timeline}: {description}")
            else:
                print(f"\n⚠ Missing expected columns")
                print(f"  Expected: 'timeline', 'description'")
                print(f"  Found: {list(df.columns)}")
        
        else:
            print("\n⚠ 'names' sheet not found")
            
            # Try to read the first sheet
            first_sheet = xl_file.sheet_names[0]
            print(f"\nReading first sheet '{first_sheet}' instead:")
            df = pd.read_excel(excel_path, sheet_name=first_sheet)
            print(f"Columns: {list(df.columns)}")
            print(f"First 5 rows:\n{df.head().to_string()}")
            
    except Exception as e:
        print(f"Error reading Excel file: {e}")

if __name__ == "__main__":
    examine_excel_file()
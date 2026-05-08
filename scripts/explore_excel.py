#!/usr/bin/env python3
"""
Excel File Explorer for Task Specifications
============================================

This script analyzes the Task specs.xlsx file to understand its structure
and content for mapping to the webapp data format.
"""

import pandas as pd
import os
from pathlib import Path

def explore_excel_file():
    """Explore the structure and content of the Task specs.xlsx file"""
    
    excel_path = Path("content/Task spec.xlsx")
    
    if not excel_path.exists():
        print(f"Error: Excel file not found at {excel_path}")
        print("Available files in content directory:")
        content_dir = Path("content")
        if content_dir.exists():
            for file in content_dir.iterdir():
                print(f"  - {file.name}")
        return
    
    print("=" * 60)
    print("EXCEL FILE EXPLORATION REPORT")
    print("=" * 60)
    print(f"File: {excel_path}")
    print(f"Size: {excel_path.stat().st_size} bytes")
    print()
    
    try:
        # Load the Excel file to see sheet names
        excel_file = pd.ExcelFile(excel_path)
        
        print(f"Number of sheets: {len(excel_file.sheet_names)}")
        print("Sheet names:")
        for i, sheet_name in enumerate(excel_file.sheet_names, 1):
            print(f"  {i}. {sheet_name}")
        print()
        
        # Analyze each sheet
        for sheet_name in excel_file.sheet_names:
            print("=" * 40)
            print(f"SHEET: {sheet_name}")
            print("=" * 40)
            
            try:
                # Read the sheet
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
                
                print(f"Dimensions: {df.shape[0]} rows × {df.shape[1]} columns")
                print()
                
                # Show column information
                print("Columns:")
                for i, col in enumerate(df.columns, 1):
                    non_null_count = df[col].count()
                    data_types = df[col].dtype
                    print(f"  {i:2d}. '{col}' ({data_types}) - {non_null_count} non-null values")
                print()
                
                # Show first few rows (preview)
                print("First 5 rows (preview):")
                print(df.head().to_string())
                print()
                
                # Show unique values for categorical-looking columns
                for col in df.columns:
                    unique_values = df[col].nunique()
                    if unique_values <= 20 and unique_values > 1:  # Likely categorical
                        print(f"Unique values in '{col}' ({unique_values} unique):")
                        unique_vals = df[col].value_counts().head(10)
                        for val, count in unique_vals.items():
                            print(f"  - '{val}': {count} occurrences")
                        if unique_values > 10:
                            print(f"  ... and {unique_values - 10} more")
                        print()
                
                # Check for empty/null data patterns
                null_counts = df.isnull().sum()
                if null_counts.any():
                    print("Missing data summary:")
                    for col, null_count in null_counts.items():
                        if null_count > 0:
                            percentage = (null_count / len(df)) * 100
                            print(f"  - '{col}': {null_count} missing ({percentage:.1f}%)")
                    print()
                
            except Exception as e:
                print(f"Error reading sheet '{sheet_name}': {e}")
                print()
        
        # Summary recommendations
        print("=" * 60)
        print("ANALYSIS SUMMARY")
        print("=" * 60)
        print("Key observations for webapp integration:")
        print()
        
        # Re-analyze for recommendations
        for sheet_name in excel_file.sheet_names:
            try:
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
                print(f"Sheet '{sheet_name}':")
                
                # Identify potential engine/category mappings
                engine_cols = [col for col in df.columns if 'engine' in col.lower() or 'e1' in str(col).lower() or 'e2' in str(col).lower()]
                category_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['category', 'type', 'section', 'about', 'parameter', 'timeline', 'data'])]
                content_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['description', 'content', 'text', 'detail', 'info'])]
                
                if engine_cols:
                    print(f"  - Potential engine identifiers: {engine_cols}")
                if category_cols:
                    print(f"  - Potential category fields: {category_cols}")
                if content_cols:
                    print(f"  - Potential content fields: {content_cols}")
                
                print(f"  - Total records: {len(df)}")
                print()
                
            except Exception:
                continue
                
    except Exception as e:
        print(f"Error analyzing Excel file: {e}")
        return
    
    print("Script completed successfully!")
    print("Next step: Create mapping document based on this analysis.")

if __name__ == "__main__":
    explore_excel_file()
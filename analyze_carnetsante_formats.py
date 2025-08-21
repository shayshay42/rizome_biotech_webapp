#!/usr/bin/env python3
"""
Analyze CarnetSante PDF Formats
Extracts and compares data from different CarnetSante report formats
"""

import re
from pathlib import Path
import sys
import pandas as pd

# Add utils to path
sys.path.append(str(Path(__file__).parent))
from utils.pdf_extraction import UniversalLabExtractor

def extract_from_all_files():
    """Extract data from all CarnetSante files and compare formats"""
    
    files = [
        "assets/carnetsante/carnetsante_sample_shayan_blood_test.pdf",  # Original format
        "assets/carnetsante/ben_carnetsante_type2.pdf",  # New Quebec Health Booklet
        "assets/carnetsante/shayan_carnetsante_type2.pdf"  # New Quebec Health Booklet
    ]
    
    extractor = UniversalLabExtractor()
    results = {}
    
    for file_path in files:
        print(f"\n{'='*60}")
        print(f"ANALYZING: {Path(file_path).name}")
        print(f"{'='*60}")
        
        try:
            result = extractor.extract_from_pdf(file_path)
            results[Path(file_path).name] = result
            
            print(f"Format detected: {result['extraction_metadata']['format']}")
            print(f"Extraction success: {result['extraction_metadata']['success']}")
            print(f"CBC tests found: {result['extraction_metadata']['cbc_tests_found']}")
            
            if result['patient_info']:
                print(f"\nPatient Info:")
                for key, value in result['patient_info'].items():
                    print(f"  {key}: {value}")
            
            if result['cbc_data']:
                print(f"\nCBC Data ({len(result['cbc_data'])} tests):")
                for test, data in result['cbc_data'].items():
                    flag_str = f" [{data['flag']}]" if data['flag'] else ""
                    print(f"  {test}: {data['value']} {data['unit']}{flag_str}")
            
            if result['additional_tests']:
                print(f"\nAdditional Tests ({len(result['additional_tests'])} tests):")
                for test, data in result['additional_tests'].items():
                    print(f"  {test}: {data['value']} {data['unit']}")
                    
        except Exception as e:
            print(f"ERROR processing {file_path}: {e}")
            results[Path(file_path).name] = {'error': str(e)}
    
    return results

def create_comparison_table(results):
    """Create a comparison table of extracted CBC values"""
    
    comparison_data = []
    
    for filename, result in results.items():
        if 'error' in result:
            continue
            
        row = {
            'filename': filename,
            'format': result['extraction_metadata']['format'],
            'success': result['extraction_metadata']['success'],
            'cbc_tests_found': result['extraction_metadata']['cbc_tests_found']
        }
        
        # Add CBC values
        cbc_data = result.get('cbc_data', {})
        for test_name in ['WBC', 'RBC', 'HGB', 'HCT', 'MCV', 'PLT', 'RDW', 'NLR', 
                         'NEUT_ABS', 'NEUT_PCT', 'LYMPH_ABS', 'LYMPH_PCT', 
                         'MONO_ABS', 'MONO_PCT', 'EOS_ABS', 'EOS_PCT']:
            if test_name in cbc_data:
                row[test_name] = cbc_data[test_name]['value']
            else:
                row[test_name] = None
        
        comparison_data.append(row)
    
    df = pd.DataFrame(comparison_data)
    return df

if __name__ == "__main__":
    print("🔬 CARNETSANTE FORMAT ANALYSIS")
    print("Analyzing all CarnetSante PDF formats to create universal extractor")
    
    # Extract from all files
    results = extract_from_all_files()
    
    # Create comparison table
    comparison_df = create_comparison_table(results)
    
    print(f"\n{'='*80}")
    print("COMPARISON TABLE")
    print(f"{'='*80}")
    print(comparison_df.to_string(index=False))
    
    # Save comparison
    output_path = Path(__file__).parent / "carnetsante_format_comparison.csv"
    comparison_df.to_csv(output_path, index=False)
    print(f"\n✅ Comparison saved to: {output_path}")
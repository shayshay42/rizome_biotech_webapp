#!/usr/bin/env python3
"""
Analyze PDF Text Structure
Examines the raw text structure of different CarnetSante formats
"""

import PyPDF2
from pathlib import Path

def analyze_pdf_text(pdf_path):
    """Extract and analyze raw text from PDF"""
    print(f"\n{'='*80}")
    print(f"ANALYZING TEXT STRUCTURE: {Path(pdf_path).name}")
    print(f"{'='*80}")
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            all_text = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                print(f"\n--- PAGE {page_num + 1} ---")
                print(text[:1000] + "..." if len(text) > 1000 else text)
                all_text += text + "\n"
        
        # Look for key patterns
        print(f"\n--- PATTERN ANALYSIS ---")
        
        # Check for different format indicators
        patterns = {
            'Quebec Health Booklet': ['Carnet santé', 'Prélèvement', 'Québec'],
            'CarnetSante Lab': ['CarnetSante', 'PATIENT EXTERNE', 'HEMATOLOGIE'],
            'CBC Markers': ['Leucocytes', 'Hémoglobine', 'Hématocrite', 'WBC', 'HGB', 'HCT'],
            'Reference Values': ['Valeur de référence', 'Reference value', 'REF.RANGE'],
            'Units': ['g/L', '10*9/L', '10*12/L', 'fL', 'pg', '%']
        }
        
        for pattern_name, keywords in patterns.items():
            found = [kw for kw in keywords if kw in all_text]
            print(f"{pattern_name}: {found}")
        
        return all_text
        
    except Exception as e:
        print(f"ERROR: {e}")
        return None

if __name__ == "__main__":
    files = [
        "/Users/shayanhajhashemi/Documents/Rhizome/assets/carnetsante/carnetsante_sample_shayan_blood_test.pdf",
        "/Users/shayanhajhashemi/Documents/Rhizome/assets/carnetsante/ben_carnetsante_type2.pdf", 
        "/Users/shayanhajhashemi/Documents/Rhizome/assets/carnetsante/shayan_carnetsante_type2.pdf"
    ]
    
    for file_path in files:
        analyze_pdf_text(file_path)
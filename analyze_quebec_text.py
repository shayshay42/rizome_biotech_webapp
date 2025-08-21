#!/usr/bin/env python3
"""
Analyze Quebec Health Booklet Text Structure
Detailed analysis to improve CBC extraction accuracy
"""

import PyPDF2
import re

def analyze_hemogramme_section(pdf_path):
    """Analyze the Hémogramme section in detail"""
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    
    lines = text.split('\n')
    
    print("ANALYZING HÉMOGRAMME SECTION")
    print("="*60)
    
    in_hemogramme = False
    for i, line in enumerate(lines):
        line = line.strip()
        
        if 'Hémogramme' in line:
            in_hemogramme = True
            print(f"\n>>> START OF HÉMOGRAMME SECTION <<<")
            continue
        
        if in_hemogramme and ('Électrolytes' in line or 'Glucides' in line):
            print(f"\n>>> END OF HÉMOGRAMME SECTION <<<")
            break
        
        if in_hemogramme:
            print(f"Line {i:3d}: {line}")
            
            # Look for specific patterns
            if any(keyword in line for keyword in ['Leucocytes', 'Hémoglobine', 'Plaquettes', 'Monocytes']):
                print(f"    ^^^ BIOMARKER DETECTED: {line}")
            
            if re.search(r'[0-9,\.]+\s*(g/L|10\*9/L|10\*12/L|fL|pg|%)', line):
                print(f"    ^^^ VALUE DETECTED: {line}")
            
            if 'Valeur de référence' in line:
                print(f"    ^^^ REFERENCE: {line}")

if __name__ == "__main__":
    pdf_path = "/Users/shayanhajhashemi/Documents/Rhizome/assets/carnetsante/shayan_carnetsante_type2.pdf"
    analyze_hemogramme_section(pdf_path)
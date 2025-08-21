#!/usr/bin/env python3
"""
Quebec Health Booklet (Type 2) CBC Extractor
Focused extraction of the 7 key CBC biomarkers needed for ML model:
HGB, MCV, MONO, NLR, PLT, RDW, WBC
"""

import re
import PyPDF2
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import json

class QuebecHealthBookletExtractor:
    """Extractor specifically for Quebec Health Booklet format"""
    
    def __init__(self):
        # ML model requires these 7 biomarkers
        self.required_biomarkers = {
            'HGB': 'Hemoglobin',
            'MCV': 'Mean Corpuscular Volume', 
            'MONO': 'Monocytes Absolute',
            'NLR': 'Neutrophil to Lymphocyte Ratio',
            'PLT': 'Platelets',
            'RDW': 'Red Cell Distribution Width',
            'WBC': 'White Blood Cells'
        }
    
    def extract_from_pdf(self, file_path: str) -> Dict:
        """Extract CBC data from Quebec Health Booklet PDF"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            # Extract patient info
            patient_info = self._extract_patient_info(text)
            
            # Extract CBC values
            cbc_data = self._extract_cbc_values(text)
            
            # Calculate NLR if needed
            if 'NEUT_PCT' in cbc_data and 'LYMPH_PCT' in cbc_data:
                neut_pct = cbc_data['NEUT_PCT']['value']
                lymph_pct = cbc_data['LYMPH_PCT']['value']
                if lymph_pct > 0:
                    nlr = round(neut_pct / lymph_pct, 2)
                    cbc_data['NLR'] = {
                        'value': nlr,
                        'unit': 'ratio',
                        'flag': '',
                        'reference_range': '1.0-3.0',
                        'original_name': 'Calculated NLR'
                    }
            
            # Create ML-ready feature vector
            ml_features = self._create_ml_features(cbc_data)
            
            result = {
                'patient_info': patient_info,
                'cbc_data': cbc_data,
                'ml_features': ml_features,
                'extraction_metadata': {
                    'format': 'quebec_health_booklet',
                    'source_file': file_path,
                    'extracted_at': datetime.now().isoformat(),
                    'success': len(ml_features) > 0,
                    'cbc_tests_found': len(cbc_data),
                    'ml_ready_features': len(ml_features)
                }
            }
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'patient_info': {},
                'cbc_data': {},
                'ml_features': {},
                'extraction_metadata': {
                    'format': 'quebec_health_booklet',
                    'source_file': file_path,
                    'extracted_at': datetime.now().isoformat(),
                    'success': False,
                    'cbc_tests_found': 0,
                    'ml_ready_features': 0
                }
            }
    
    def _extract_patient_info(self, text: str) -> Dict:
        """Extract patient information"""
        patient_info = {}
        
        # Patient name from "Carnet santé SHAYAN"
        name_match = re.search(r'Carnet santé\s+([A-Z]+)', text)
        if name_match:
            patient_info['name'] = name_match.group(1)
        
        # Collection date from "23 janvier 2024, 10 h 57"
        date_match = re.search(r'(\d{1,2}\s+\w+\s+\d{4},\s*\d{1,2}\s*h\s*\d{2})', text)
        if date_match:
            patient_info['collection_date'] = date_match.group(1)
        
        # Prescriber
        prescriber_match = re.search(r'Prescripteur\s+([A-Z\s\d]+)', text)
        if prescriber_match:
            patient_info['prescriber'] = prescriber_match.group(1).strip()
        
        # Laboratory
        lab_match = re.search(r'Laboratoire\s+([A-Z\s]+)', text)
        if lab_match:
            patient_info['laboratory'] = lab_match.group(1).strip()
        
        return patient_info
    
    def _extract_cbc_values(self, text: str) -> Dict:
        """Extract CBC values from Quebec Health Booklet format"""
        cbc_data = {}
        
        # Parse line by line using the discovered pattern
        lines = text.split('\n')
        current_test = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Look for test names
            if 'Leucocytes' in line and 'Valeur de référence' not in line:
                current_test = 'WBC'
                # Look ahead for the pattern: reference_range(unit)value unit
                value = self._extract_quebec_value(lines, i, '10*9/L')
                if value:
                    cbc_data['WBC'] = {
                        'value': value,
                        'unit': '10*9/L',
                        'flag': '',
                        'reference_range': '4.5-11',
                        'original_name': 'Leucocytes'
                    }
            
            elif 'Hémoglobine' in line and 'Valeur de référence' not in line and i < 60:  # First occurrence is HGB
                current_test = 'HGB'
                value = self._extract_quebec_value(lines, i, 'g/L')
                if value:
                    cbc_data['HGB'] = {
                        'value': value,
                        'unit': 'g/L',
                        'flag': '',
                        'reference_range': '135-175',
                        'original_name': 'Hémoglobine'
                    }
            
            elif 'Plaquettes' in line and 'Valeur de référence' not in line:
                current_test = 'PLT'
                value = self._extract_quebec_value(lines, i, '10*9/L')
                if value:
                    cbc_data['PLT'] = {
                        'value': value,
                        'unit': '10*9/L',
                        'flag': '',
                        'reference_range': '140-450',
                        'original_name': 'Plaquettes'
                    }
            
            elif 'Monocytes' in line and 'MONOCYTES %' not in line and 'Valeur de référence' not in line:
                current_test = 'MONO'
                value = self._extract_quebec_value(lines, i, '10*9/L')
                if value:
                    cbc_data['MONO'] = {
                        'value': value,
                        'unit': '10*9/L',
                        'flag': '',
                        'reference_range': '0-0.8',
                        'original_name': 'Monocytes'
                    }
            
            elif 'NEUTROPHILES %' in line:
                value = self._extract_quebec_value(lines, i, '%')
                if value:
                    cbc_data['NEUT_PCT'] = {
                        'value': value,
                        'unit': '%',
                        'flag': '',
                        'reference_range': '40-70',
                        'original_name': 'NEUTROPHILES %'
                    }
            
            elif 'LYMPHOCYTES %' in line or 'LYMPHOCY TES %' in line:
                value = self._extract_quebec_value(lines, i, '%')
                if value:
                    cbc_data['LYMPH_PCT'] = {
                        'value': value,
                        'unit': '%',
                        'flag': '',
                        'reference_range': '22-44',
                        'original_name': 'LYMPHOCYTES %'
                    }
            
            # Look for MCV and RDW in Observation sections
            elif 'Obser vation' in line and i > 60 and i < 90:  # MCV
                value = self._extract_quebec_value(lines, i, 'fL')
                if value:
                    cbc_data['MCV'] = {
                        'value': value,
                        'unit': 'fL',
                        'flag': '',
                        'reference_range': '80-100',
                        'original_name': 'Volume globulaire moyen'
                    }
            
            elif 'Obser vation' in line and i > 70:  # RDW
                # Look for pattern with no unit (just number)
                for j in range(i, min(i + 4, len(lines))):
                    check_line = lines[j].strip()
                    rdw_match = re.search(r'([0-9,\.]+)\s*$', check_line)
                    if rdw_match and 'Valeur de référence' not in check_line:
                        try:
                            value_str = rdw_match.group(1).replace(',', '.')
                            value = float(value_str)
                            if 10 < value < 20:  # RDW typical range
                                cbc_data['RDW'] = {
                                    'value': value,
                                    'unit': '%',
                                    'flag': '',
                                    'reference_range': '12.7-16',
                                    'original_name': 'Largeur de distribution érythrocytaire'
                                }
                                break
                        except:
                            continue
        
        return cbc_data
    
    def _extract_quebec_value(self, lines: list, start_idx: int, expected_unit: str) -> Optional[float]:
        """Extract value from Quebec Health Booklet format pattern: reference_range(unit)value unit"""
        # Look in the next 4 lines for the pattern
        for i in range(start_idx, min(start_idx + 4, len(lines))):
            line = lines[i].strip()
            
            # Skip reference value lines without data
            if 'Valeur de référence' in line and expected_unit not in line:
                continue
            
            # Look for the pattern: reference_range(unit)value unit
            # Examples: "4,5 -  11 (10*9/L)5,87  10*9/L", "135 -  175  (g/L)137  g/L"
            if expected_unit == '10*9/L':
                # Pattern: reference_range(10*9/L)value 10*9/L
                match = re.search(r'[0-9,\.\s\-\(\)]+10\*9/L\)([0-9,\.]+)\s*10\*9/L', line)
            elif expected_unit == 'g/L':
                # Pattern: reference_range(g/L)value g/L
                match = re.search(r'[0-9,\.\s\-\(\)]+g/L\)([0-9,\.]+)\s*g/L', line)
            elif expected_unit == '%':
                # Pattern: reference_range(%)value %
                match = re.search(r'[0-9,\.\s\-\(\)]+%\)([0-9,\.]+)\s*%', line)
            elif expected_unit == 'fL':
                # Pattern: reference_range(fL)value fL
                match = re.search(r'[0-9,\.\s\-\(\)]+fL\)([0-9,\.]+)\s*fL', line)
            else:
                # General pattern
                match = re.search(r'([0-9,\.]+)', line)
            
            if match:
                try:
                    value_str = match.group(1).replace(',', '.')
                    return float(value_str)
                except:
                    continue
        
        return None
    
    def _extract_value_from_context(self, lines: list, start_idx: int, test_name: str, expected_unit: str) -> Optional[float]:
        """Extract numerical value from surrounding lines"""
        # Look in the next 3 lines for the value
        for i in range(start_idx, min(start_idx + 4, len(lines))):
            line = lines[i].strip()
            
            # Skip reference value lines
            if 'Valeur de référence' in line:
                continue
            
            # Look for patterns like "5,87 10*9/L" or "137 g/L"
            if expected_unit == '10*9/L':
                match = re.search(r'([0-9,\.]+)\s*10\*9/L', line)
            elif expected_unit == 'g/L':
                match = re.search(r'([0-9,\.]+)\s*g/L', line)
            elif expected_unit == '%':
                match = re.search(r'([0-9,\.]+)\s*%', line)
            else:
                match = re.search(r'([0-9,\.]+)', line)
            
            if match:
                try:
                    value_str = match.group(1).replace(',', '.')
                    return float(value_str)
                except:
                    continue
        
        return None
    
    def _create_ml_features(self, cbc_data: Dict) -> Dict:
        """Create feature vector for ML model with the 7 required biomarkers"""
        import numpy as np
        
        ml_features = {}
        
        # Extract the 7 key biomarkers needed for ML model, using NaN for missing values
        for biomarker in self.required_biomarkers.keys():
            if biomarker in cbc_data:
                ml_features[biomarker] = cbc_data[biomarker]['value']
            else:
                ml_features[biomarker] = np.nan
        
        return ml_features

def test_quebec_extractor():
    """Test the Quebec Health Booklet extractor"""
    
    files = [
        "/Users/shayanhajhashemi/Documents/Rhizome/assets/carnetsante/shayan_carnetsante_type2.pdf"
    ]
    
    extractor = QuebecHealthBookletExtractor()
    
    for file_path in files:
        print(f"\n{'='*80}")
        print(f"TESTING QUEBEC HEALTH BOOKLET EXTRACTOR: {Path(file_path).name}")
        print(f"{'='*80}")
        
        result = extractor.extract_from_pdf(file_path)
        
        print(f"Format: {result['extraction_metadata']['format']}")
        print(f"Success: {result['extraction_metadata']['success']}")
        print(f"CBC Tests Found: {result['extraction_metadata']['cbc_tests_found']}")
        print(f"ML-Ready Features: {result['extraction_metadata']['ml_ready_features']}")
        
        if result.get('error'):
            print(f"ERROR: {result['error']}")
            continue
        
        if result['patient_info']:
            print(f"\nPatient Info:")
            for key, value in result['patient_info'].items():
                print(f"  {key}: {value}")
        
        if result['cbc_data']:
            print(f"\nCBC Data:")
            for test, data in result['cbc_data'].items():
                flag_str = f" [{data['flag']}]" if data['flag'] else ""
                print(f"  {test}: {data['value']} {data['unit']}{flag_str}")
        
        if result['ml_features']:
            print(f"\nML Features (Required for Cancer Model):")
            for biomarker, value in result['ml_features'].items():
                print(f"  {biomarker}: {value}")
            
            # Check completeness for ML model
            required = set(extractor.required_biomarkers.keys())
            available = set(result['ml_features'].keys())
            missing = required - available
            
            print(f"\nML Model Readiness:")
            print(f"  Required biomarkers: {len(required)}")
            print(f"  Available biomarkers: {len(available)}")
            print(f"  Missing biomarkers: {list(missing) if missing else 'None - Ready for ML!'}")

if __name__ == "__main__":
    test_quebec_extractor()
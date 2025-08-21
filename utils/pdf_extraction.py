"""
Enhanced PDF Extraction for Multiple Lab Report Formats
Supports CarnetSante and other lab report formats with intelligent field mapping
"""

import re
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import PyPDF2
from pathlib import Path
import json
from datetime import datetime

class LabValueMapping:
    """Handles mapping between different lab report naming conventions"""
    
    def __init__(self):
        # Standard CBC biomarker names used in our system
        self.standard_names = {
            'WBC': 'White Blood Cells',
            'RBC': 'Red Blood Cells', 
            'HGB': 'Hemoglobin',
            'HCT': 'Hematocrit',
            'MCV': 'Mean Corpuscular Volume',
            'MCH': 'Mean Corpuscular Hemoglobin',
            'MCHC': 'Mean Corpuscular Hemoglobin Concentration',
            'RDW': 'Red Cell Distribution Width',
            'PLT': 'Platelets',
            'MPV': 'Mean Platelet Volume',
            'NEUT_ABS': 'Neutrophils Absolute',
            'NEUT_PCT': 'Neutrophils Percentage',
            'LYMPH_ABS': 'Lymphocytes Absolute',
            'LYMPH_PCT': 'Lymphocytes Percentage',
            'MONO_ABS': 'Monocytes Absolute',
            'MONO_PCT': 'Monocytes Percentage',
            'EOS_ABS': 'Eosinophils Absolute',
            'EOS_PCT': 'Eosinophils Percentage',
            'BASO_ABS': 'Basophils Absolute',
            'BASO_PCT': 'Basophils Percentage',
            'NLR': 'Neutrophil to Lymphocyte Ratio'
        }
        
        # CarnetSante specific mappings
        self.carnetsante_mapping = {
            'GB': 'WBC',
            'WBC': 'WBC',
            'HB': 'HGB', 
            'HGB': 'HGB',
            'HT': 'HCT',
            'HCT': 'HCT',
            'GR': 'RBC',
            'RBC': 'RBC',
            'VGM': 'MCV',
            'MCV': 'MCV',
            'TGMH': 'MCH',
            'MCH': 'MCH',
            'CCMH': 'MCHC',
            'MCHC': 'MCHC',
            'DVE': 'RDW',
            'RDW': 'RDW',
            'PLAQ': 'PLT',
            'PLAT': 'PLT',
            'PLT': 'PLT',
            'VPM': 'MPV',
            'MPV': 'MPV',
            'Neutrophiles abs.': 'NEUT_ABS',
            'Neutrophiles Rel.': 'NEUT_PCT',
            'Lymphocytes abs.': 'LYMPH_ABS',
            'Lymphocytes Rel.': 'LYMPH_PCT',
            'Monocytes abs.': 'MONO_ABS',
            'Monocytes Rel.': 'MONO_PCT',
            'Eosinophiles abs.': 'EOS_ABS',
            'Eosinophiles Rel.': 'EOS_PCT',
            'Basophiles abs.': 'BASO_ABS',
            'Basophiles Rel.': 'BASO_PCT',
            'NRBC abs.': 'NRBC_ABS',
            'NRBC Rel.': 'NRBC_PCT'
        }
        
        # Alternative naming patterns (case insensitive)
        self.pattern_mapping = {
            r'white.*blood.*cell': 'WBC',
            r'red.*blood.*cell': 'RBC',
            r'hemoglobin': 'HGB',
            r'hematocrit': 'HCT',
            r'platelet': 'PLT',
            r'neutrophil.*abs': 'NEUT_ABS',
            r'neutrophil.*rel|neutrophil.*%': 'NEUT_PCT',
            r'lymphocyte.*abs': 'LYMPH_ABS',
            r'lymphocyte.*rel|lymphocyte.*%': 'LYMPH_PCT',
            r'monocyte.*abs': 'MONO_ABS',
            r'monocyte.*rel|monocyte.*%': 'MONO_PCT',
            r'eosinophil.*abs': 'EOS_ABS',
            r'eosinophil.*rel|eosinophil.*%': 'EOS_PCT',
            r'basophil.*abs': 'BASO_ABS',
            r'basophil.*rel|basophil.*%': 'BASO_PCT'
        }
        
        # Unit normalization
        self.unit_conversions = {
            'g/dL': {'to_g/L': 10.0},
            'mg/dL': {'to_g/L': 0.01},
            'K/uL': {'to_10^9/L': 1.0},
            'M/uL': {'to_10^12/L': 1.0},
            '10^3/uL': {'to_10^9/L': 1.0},
            '10^6/uL': {'to_10^12/L': 1.0}
        }

    def normalize_test_name(self, test_name: str) -> Optional[str]:
        """Convert any test name to standard format"""
        # Direct mapping first
        if test_name in self.carnetsante_mapping:
            return self.carnetsante_mapping[test_name]
        
        # Pattern matching
        test_lower = test_name.lower()
        for pattern, standard_name in self.pattern_mapping.items():
            if re.search(pattern, test_lower):
                return standard_name
        
        return None

    def normalize_units(self, value: float, from_unit: str, target_unit: str) -> float:
        """Convert between different units"""
        if from_unit == target_unit:
            return value
        
        if from_unit in self.unit_conversions:
            conversion_key = f'to_{target_unit}'
            if conversion_key in self.unit_conversions[from_unit]:
                return value * self.unit_conversions[from_unit][conversion_key]
        
        return value

class CarnetSanteExtractor:
    """Specialized extractor for CarnetSante lab reports"""
    
    def __init__(self):
        self.mapping = LabValueMapping()
        
    def extract_patient_info(self, text: str) -> Dict:
        """Extract patient demographics"""
        patient_info = {}
        
        # Patient name
        name_match = re.search(r'PATIENT EXTERNE\s+([A-Z]+,\s*[A-Z]+)', text)
        if name_match:
            patient_info['name'] = name_match.group(1)
        
        # Date of birth and age
        dob_match = re.search(r'NÈ\(e\)/DOB:\s*(\d{4}/\d{2}/\d{2})', text)
        if dob_match:
            patient_info['dob'] = dob_match.group(1)
        
        age_match = re.search(r'Age:\s*(\d+)', text)
        if age_match:
            patient_info['age'] = int(age_match.group(1))
        
        # Sex
        sex_match = re.search(r'Sex\(e\):\s*([MF])', text)
        if sex_match:
            patient_info['sex'] = sex_match.group(1)
        
        # Collection date
        collected_match = re.search(r'PRÈLEVÈ/COLLECTED\s*(\d{4}/\d{2}/\d{2}\s*\d{2}:\d{2})', text)
        if collected_match:
            patient_info['collection_date'] = collected_match.group(1)
        
        return patient_info

    def extract_cbc_values(self, text: str) -> Dict:
        """Extract CBC values from CarnetSante format with enhanced parsing"""
        cbc_data = {}
        
        # Split text into lines for easier processing
        lines = text.split('\n')
        
        # Find hematology section
        in_hematology = False
        found_fsc_cbc = False
        
        for line in lines:
            line = line.strip()
            
            # Check if we're in the hematology section
            if 'H E M A T O L O G I E' in line or 'H E M A T O L O G Y' in line:
                in_hematology = True
                continue
            
            # Look for the FSC/CBC subsection
            if in_hematology and ('FSC / CBC' in line or 'FSC/CBC' in line):
                found_fsc_cbc = True
                continue
            
            # Stop when we reach another section
            if in_hematology and ('B I O C H I M I E' in line or 'suite à la page suivante' in line):
                break
            
            if not in_hematology or not found_fsc_cbc:
                continue
            
            # Skip header lines
            if any(x in line for x in ['ANALYSE(S)', 'TEST(S)', 'RÉSULTAT', 'RESULT', 'FLAG', 'UNITS', 'REF.RANGE']):
                continue
            
            # Debug: print line for troubleshooting
            print(f"Processing CBC line: {line}")
            
            # CarnetSante specific patterns based on the actual PDF format
            # Pattern 1: Basic CBC values like "GB WBC 5.87 10^9/L 4.50-11.00 RADVS"
            match1 = re.search(r'^([A-Z]+)\s+([A-Z]+)\s+([0-9\.]+)\s*([LH]?)\s*([a-zA-Z0-9\^\\/]*)\s+([0-9\.\-]+)\s*([A-Z]*)', line)
            
            # Pattern 2: Differential counts with "abs." like "Neutrophiles abs. Auto 3.72 10^9/L 1.80-7.70 RADVS"
            match2 = re.search(r'^([A-Za-z]+)\s+abs\.\s+Auto\s+([0-9\.]+)\s*([LH]?)\s*([a-zA-Z0-9\^\\/]*)\s+([0-9\.\-]+)\s*([A-Z]*)', line)
            
            # Pattern 3: Relative percentages like "Neutrophiles Rel. 63.31 % 40.00-70.00 RADVS"
            match3 = re.search(r'^([A-Za-z]+)\s+Rel\.\s+([0-9\.]+)\s*([LH]?)\s*%\s+([0-9\.\-]+)\s*([A-Z]*)', line)
            
            # Pattern 4: Special cases like "DVE RDW 13.3 12.7-16.0 RADVS"
            match4 = re.search(r'^([A-Z]+)\s+([A-Z]+)\s+([0-9\.]+)\s+([0-9\.\-]+)\s*([A-Z]*)', line)
            
            # Pattern 5: NRBC special format like "NRBC abs. Auto 0.00 10^9/L RADVS"
            match5 = re.search(r'^(NRBC)\s+(abs|Rel)\.\s+Auto\s+([0-9\.]+)\s*([a-zA-Z0-9\^\\/\%]*)\s*([A-Z]*)', line)
            
            match = match1 or match2 or match3 or match4 or match5
            
            if match:
                groups = match.groups()
                
                try:
                    # Determine which match pattern was used and extract accordingly
                    if match1:
                        # Pattern: "GB WBC 5.87 10^9/L 4.50-11.00 RADVS"
                        french_name, english_name = groups[0], groups[1]
                        test_name = english_name  # Use English name for mapping
                        value = float(groups[2])
                        flag = groups[3] if groups[3] else ''
                        unit = groups[4] if groups[4] else ''
                        reference_range = groups[5] if groups[5] else ''
                        
                    elif match2:
                        # Pattern: "Neutrophiles abs. Auto 3.72 10^9/L 1.80-7.70 RADVS"
                        test_name = f"{groups[0]} abs."
                        value = float(groups[1])
                        flag = groups[2] if groups[2] else ''
                        unit = groups[3] if groups[3] else ''
                        reference_range = groups[4] if groups[4] else ''
                        
                    elif match3:
                        # Pattern: "Neutrophiles Rel. 63.31 % 40.00-70.00 RADVS"
                        test_name = f"{groups[0]} Rel."
                        value = float(groups[1])
                        flag = groups[2] if groups[2] else ''
                        unit = '%'
                        reference_range = groups[3] if groups[3] else ''
                        
                    elif match4:
                        # Pattern: "DVE RDW 13.3 12.7-16.0 RADVS"
                        french_name, english_name = groups[0], groups[1]
                        test_name = english_name
                        value = float(groups[2])
                        flag = ''
                        unit = ''  # Will be inferred
                        reference_range = groups[3] if groups[3] else ''
                        
                    elif match5:
                        # Pattern: "NRBC abs. Auto 0.00 10^9/L RADVS"
                        test_name = f"{groups[0]} {groups[1]}."
                        value = float(groups[2])
                        flag = ''
                        unit = groups[3] if groups[3] else ''
                        reference_range = ''
                        
                    else:
                        continue
                    
                    # Normalize test name to standard format
                    standard_name = self.mapping.normalize_test_name(test_name)
                    if standard_name:
                        cbc_data[standard_name] = {
                            'value': value,
                            'unit': unit,
                            'flag': flag,
                            'reference_range': reference_range,
                            'original_name': test_name,
                            'collection_timestamp': self._extract_collection_time(text)
                        }
                        print(f"✓ Extracted: {test_name} -> {standard_name} = {value} {unit}")
                    else:
                        print(f"✗ No mapping found for: {test_name}")
                        
                except (ValueError, IndexError) as e:
                    print(f"Error parsing line '{line}': {e}")
                    continue
        
        # Calculate NLR if we have neutrophil and lymphocyte percentages
        if 'NEUT_PCT' in cbc_data and 'LYMPH_PCT' in cbc_data:
            if cbc_data['LYMPH_PCT']['value'] > 0:
                nlr = cbc_data['NEUT_PCT']['value'] / cbc_data['LYMPH_PCT']['value']
                cbc_data['NLR'] = {
                    'value': round(nlr, 2),
                    'unit': 'ratio',
                    'flag': '',
                    'reference_range': '1.0-3.0',
                    'original_name': 'Calculated NLR',
                    'collection_timestamp': cbc_data['NEUT_PCT'].get('collection_timestamp')
                }
        
        return cbc_data
    
    def _extract_collection_time(self, text: str) -> str:
        """Extract collection timestamp from PDF"""
        # Look for collection date/time patterns
        patterns = [
            r'PRÈLEVÈ/COLLECTED\s*(\d{4}/\d{2}/\d{2}\s*\d{2}:\d{2})',
            r'Collection.*?(\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2})',
            r'(\d{4}/\d{2}/\d{2}\s*\d{2}:\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return datetime.now().strftime('%Y/%m/%d %H:%M')

    def extract_additional_tests(self, text: str) -> Dict:
        """Extract additional biochemistry and other tests"""
        additional_tests = {}
        
        # Common additional tests to extract
        test_patterns = {
            'GLUCOSE': r'GLUCOSE\s+([0-9\.]+)\s*([a-zA-Z\/]+)',
            'CREATININE': r'CREATININE\s+([0-9\.]+)\s*([a-zA-Z\/]+)',
            'SODIUM': r'SODIUM\s+([0-9\.]+)\s*([a-zA-Z\/]+)',
            'POTASSIUM': r'POTASSIUM\s+([0-9\.]+)\s*([a-zA-Z\/]+)',
            'CHOLESTEROL': r'CHOLESTEROL\s+([0-9\.]+)\s*([a-zA-Z\/]+)',
            'TSH': r'TSH\s+([0-9\.]+)\s*([a-zA-Z\/]+)',
            'B12': r'VIT B12\s+([0-9\.]+)\s*([a-zA-Z\/]+)',
            'FERRITIN': r'FERRITINE\s+([0-9\.]+)\s*([a-zA-Z\/]+)',
            'HBA1C': r'HBA1C\s+([0-9\.]+)\s*([%])',
        }
        
        for test_name, pattern in test_patterns.items():
            match = re.search(pattern, text)
            if match:
                additional_tests[test_name] = {
                    'value': float(match.group(1)),
                    'unit': match.group(2) if len(match.groups()) > 1 else '',
                    'test_type': 'biochemistry'
                }
        
        return additional_tests

class UniversalLabExtractor:
    """Universal extractor that can handle multiple lab report formats"""
    
    def __init__(self):
        self.carnetsante_extractor = CarnetSanteExtractor()
        
    def detect_format(self, text: str) -> str:
        """Detect the format of the lab report"""
        if 'CarnetSante' in text or 'Centre de santé' in text:
            return 'carnetsante'
        elif 'PATIENT EXTERNE' in text and 'HEMATOLOGIE' in text:
            return 'carnetsante'
        else:
            return 'unknown'
    
    def extract_from_pdf(self, file_path: str) -> Dict:
        """Extract data from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            
            return self.extract_from_text(text, file_path)
        
        except Exception as e:
            return {
                'error': f"Failed to extract from PDF: {str(e)}",
                'patient_info': {},
                'cbc_data': {},
                'additional_tests': {},
                'extraction_metadata': {
                    'format': 'unknown',
                    'extracted_at': datetime.now().isoformat()
                }
            }
    
    def extract_from_text(self, text: str, source_file: str = '') -> Dict:
        """Extract data from text content"""
        format_type = self.detect_format(text)
        
        extraction_result = {
            'patient_info': {},
            'cbc_data': {},
            'additional_tests': {},
            'extraction_metadata': {
                'format': format_type,
                'source_file': source_file,
                'extracted_at': datetime.now().isoformat()
            }
        }
        
        try:
            if format_type == 'carnetsante':
                extraction_result['patient_info'] = self.carnetsante_extractor.extract_patient_info(text)
                extraction_result['cbc_data'] = self.carnetsante_extractor.extract_cbc_values(text)
                extraction_result['additional_tests'] = self.carnetsante_extractor.extract_additional_tests(text)
            
            # Add success flag
            extraction_result['extraction_metadata']['success'] = True
            extraction_result['extraction_metadata']['cbc_tests_found'] = len(extraction_result['cbc_data'])
            
        except Exception as e:
            extraction_result['error'] = str(e)
            extraction_result['extraction_metadata']['success'] = False
        
        return extraction_result

def create_standardized_cbc_vector(cbc_data: Dict) -> Dict:
    """Create standardized CBC feature vector for ML processing"""
    
    # Standard CBC features we expect
    standard_features = {
        'WBC': {'default': 7.0, 'unit': '10^9/L'},
        'RBC': {'default': 4.5, 'unit': '10^12/L'},
        'HGB': {'default': 140, 'unit': 'g/L'},
        'HCT': {'default': 0.42, 'unit': 'L'},
        'MCV': {'default': 90, 'unit': 'fL'},
        'MCH': {'default': 30, 'unit': 'pg'},
        'MCHC': {'default': 340, 'unit': 'g/L'},
        'RDW': {'default': 13.5, 'unit': '%'},
        'PLT': {'default': 250, 'unit': '10^9/L'},
        'MPV': {'default': 9.0, 'unit': 'fL'},
        'NEUT_ABS': {'default': 4.0, 'unit': '10^9/L'},
        'NEUT_PCT': {'default': 60, 'unit': '%'},
        'LYMPH_ABS': {'default': 2.0, 'unit': '10^9/L'},
        'LYMPH_PCT': {'default': 30, 'unit': '%'},
        'MONO_ABS': {'default': 0.5, 'unit': '10^9/L'},
        'MONO_PCT': {'default': 7, 'unit': '%'},
        'EOS_ABS': {'default': 0.2, 'unit': '10^9/L'},
        'EOS_PCT': {'default': 3, 'unit': '%'},
        'BASO_ABS': {'default': 0.1, 'unit': '10^9/L'},
        'BASO_PCT': {'default': 1, 'unit': '%'},
        'NLR': {'default': 2.0, 'unit': 'ratio'}
    }
    
    standardized_vector = {}
    
    for feature, info in standard_features.items():
        if feature in cbc_data:
            standardized_vector[feature] = cbc_data[feature]['value']
        else:
            # Use default value if not found
            standardized_vector[feature] = info['default']
    
    return standardized_vector

def test_extraction():
    """Test the extraction on the CarnetSante sample"""
    extractor = UniversalLabExtractor()
    
    # Test file path
    test_file = "/Users/shayanhajhashemi/Documents/Rhizome/assets/carnetsante/carnetsante_sample_shayan_blood_test.pdf"
    
    result = extractor.extract_from_pdf(test_file)
    
    print("Extraction Results:")
    print("=" * 50)
    print(f"Format: {result['extraction_metadata']['format']}")
    print(f"Success: {result['extraction_metadata']['success']}")
    print(f"CBC Tests Found: {result['extraction_metadata']['cbc_tests_found']}")
    
    print("\nPatient Info:")
    for key, value in result['patient_info'].items():
        print(f"  {key}: {value}")
    
    print("\nCBC Data:")
    for test, data in result['cbc_data'].items():
        print(f"  {test}: {data['value']} {data['unit']} [{data['flag']}]")
    
    print("\nAdditional Tests:")
    for test, data in result['additional_tests'].items():
        print(f"  {test}: {data['value']} {data['unit']}")
    
    # Create standardized vector
    standardized = create_standardized_cbc_vector(result['cbc_data'])
    print("\nStandardized CBC Vector:")
    for feature, value in standardized.items():
        print(f"  {feature}: {value}")
    
    return result

if __name__ == "__main__":
    test_extraction()
#!/usr/bin/env python3
"""
Universal CarnetSante Extractor
Handles both traditional lab reports and Quebec Health Booklet formats
"""

import re
import unicodedata
import PyPDF2
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import json

class UniversalCarnetSanteExtractor:
    """Universal extractor for all CarnetSante formats"""
    
    def __init__(self):
        # Standard CBC biomarker mappings
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
        
        # Mappings for both formats
        self.test_mappings = {
            # Traditional lab format (French/English pairs)
            'GB': 'WBC', 'WBC': 'WBC',
            'HB': 'HGB', 'HGB': 'HGB',
            'HT': 'HCT', 'HCT': 'HCT',
            'GR': 'RBC', 'RBC': 'RBC',
            'VGM': 'MCV', 'MCV': 'MCV',
            'TGMH': 'MCH', 'MCH': 'MCH',
            'CCMH': 'MCHC', 'MCHC': 'MCHC',
            'DVE': 'RDW', 'RDW': 'RDW',
            'PLAQ': 'PLT', 'PLAT': 'PLT', 'PLT': 'PLT',
            'VPM': 'MPV', 'MPV': 'MPV',
            
            # Quebec Health Booklet format (French names)
            'Leucocytes': 'WBC',
            'Hémoglobine': 'HGB',
            'Hématocrite': 'HCT',
            'Érythrocytes': 'RBC',
            'Plaquettes': 'PLT',
            'Plaquette': 'MPV',  # Mean Platelet Volume
            'Neutrophiles': 'NEUT_ABS',
            'NEUTROPHILES %': 'NEUT_PCT',
            'Lymphocytes': 'LYMPH_ABS',
            'LYMPHOCYTES %': 'LYMPH_PCT',
            'Monocytes': 'MONO_ABS',
            'MONOCYTES %': 'MONO_PCT',
            'Éosinophiles': 'EOS_ABS',
            'EOSINPHILE %': 'EOS_PCT',
            'Basophiles': 'BASO_ABS',
            'BASOPHILES %': 'BASO_PCT',
            
            # Differential counts from traditional format
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
            'NRBC Rel.': 'NRBC_PCT',
            'NRBC Abs': 'NRBC_ABS',
            'NRBC REL.': 'NRBC_PCT'
        }
    
    def _normalize_text(self, text: str) -> str:
        normalized = unicodedata.normalize('NFKD', text)
        return normalized.encode('ascii', 'ignore').decode('ascii').lower()

    def detect_format(self, text: str) -> str:
        """Detect which CarnetSante format we're dealing with"""
        normalized = self._normalize_text(text)

        if 'carnet sante' in normalized and ('hemogramme' in normalized or 'hematology' in normalized):
            return 'quebec_health_booklet'

        if 'patient externe' in normalized and ('hematologie' in normalized or 'hematology' in normalized):
            return 'traditional_lab'

        if 'carnet sante' in normalized:
            return 'quebec_health_booklet'

        return 'unknown'
    
    def extract_patient_info_traditional(self, text: str) -> Dict:
        """Extract patient info from traditional lab format"""
        patient_info = {}
        
        # Patient name
        name_match = re.search(r'PATIENT EXTERNE\s+([A-Z]+,\s*[A-Z]+)', text)
        if name_match:
            patient_info['name'] = name_match.group(1)
        
        # Date of birth and age
        dob_match = re.search(r'Né\(e\)/DOB:\s*(\d{4}/\d{2}/\d{2})', text)
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
        collected_match = re.search(r'PRÉLEVÉ/COLLECTED\s*(\d{4}/\d{2}/\d{2}\s*\d{2}:\d{2})', text)
        if collected_match:
            patient_info['collection_date'] = collected_match.group(1)
        
        return patient_info
    
    def extract_patient_info_booklet(self, text: str) -> Dict:
        """Extract patient info from Quebec Health Booklet format"""
        patient_info = {}
        
        # Patient name
        name_match = re.search(r'Carnet santé\s+([A-Z]+)', text)
        if name_match:
            patient_info['name'] = name_match.group(1)
        
        # Collection date
        date_match = re.search(r'(\d{1,2}\s+\w+\s+\d{4},\s*\d{1,2}\s*h\s*\d{2})', text)
        if date_match:
            patient_info['collection_date'] = date_match.group(1)
        
        return patient_info
    
    def extract_cbc_traditional(self, text: str) -> Dict:
        """Extract CBC from traditional lab format"""
        cbc_data = {}
        lines = text.split('\n')
        
        in_hematology = False
        found_fsc_cbc = False
        
        for line in lines:
            line = line.strip()
            
            if 'H E M A T O L O G I E' in line or 'H E M A T O L O G Y' in line:
                in_hematology = True
                continue
            
            if in_hematology and ('FSC / CBC' in line or 'FSC/CBC' in line):
                found_fsc_cbc = True
                continue
            
            if in_hematology and ('B I O C H I M I E' in line or 'suite à la page suivante' in line):
                break
            
            if not in_hematology or not found_fsc_cbc:
                continue
            
            # Skip header lines
            if any(x in line for x in ['ANALYSE(S)', 'TEST(S)', 'RÉSULTAT', 'RESULT']):
                continue
            
            # Parse different line formats
            parsed_value = self._parse_traditional_line(line)
            if parsed_value:
                test_name, value, unit, flag, ref_range = parsed_value
                standard_name = self.test_mappings.get(test_name)
                
                if standard_name:
                    cbc_data[standard_name] = {
                        'value': value,
                        'unit': unit,
                        'flag': flag,
                        'reference_range': ref_range,
                        'original_name': test_name
                    }
        
        return cbc_data
    
    def extract_cbc_booklet(self, text: str) -> Dict:
        """Extract CBC from Quebec Health Booklet format"""
        cbc_data = {}
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Look for test names and extract values
            if 'Leucocytes' in line and 'Valeur de référence' not in line:
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
                value = self._extract_quebec_value(lines, i, '10*9/L')
                if value:
                    cbc_data['MONO_ABS'] = {
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
            
            # Look for MCV in Observation sections
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
    
    def _parse_traditional_line(self, line: str) -> Optional[tuple]:
        """Parse traditional lab format line"""
        # Pattern 1: Basic CBC values like "GB WBC 5.87 10^9/L 4.50-11.00 RADVS"
        match1 = re.search(r'^([A-Z]+)\s+([A-Z]+)\s+([0-9\.]+)\s*([LH]?)\s*([a-zA-Z0-9\^\\/]*)\s+([0-9\.\-]+)', line)
        
        # Pattern 2: Differential counts like "Neutrophiles abs. Auto 3.72 10^9/L 1.80-7.70 RADVS"
        match2 = re.search(r'^([A-Za-z]+)\s+abs\.\s+Auto\s+([0-9\.]+)\s*([LH]?)\s*([a-zA-Z0-9\^\\/]*)\s+([0-9\.\-]+)', line)
        
        # Pattern 3: Relative percentages like "Neutrophiles Rel. 63.31 % 40.00-70.00 RADVS"
        match3 = re.search(r'^([A-Za-z]+)\s+Rel\.\s+([0-9\.]+)\s*([LH]?)\s*%\s+([0-9\.\-]+)', line)
        
        if match1:
            groups = match1.groups()
            test_name = groups[1]  # Use English name
            return (test_name, float(groups[2]), groups[4], groups[3], groups[5])
        elif match2:
            groups = match2.groups()
            test_name = f"{groups[0]} abs."
            return (test_name, float(groups[1]), groups[3], groups[2], groups[4])
        elif match3:
            groups = match3.groups()
            test_name = f"{groups[0]} Rel."
            return (test_name, float(groups[1]), '%', groups[2], groups[3])
        
        return None
    
    def _parse_booklet_line(self, line: str) -> Optional[tuple]:
        """Parse Quebec Health Booklet format line"""
        # Look for patterns like:
        # "Leucocytes" followed by value and reference
        # "5,87 10*9/L" and "Valeur de référence 4,5 - 11 (10*9/L)"
        
        # Pattern 1: Test name only (look for next lines for value)
        if re.match(r'^[A-ZÀ-ÿ][a-zà-ÿ\s%]+$', line) and 'Valeur de référence' not in line:
            # This might be a test name, but we need the value from subsequent lines
            pass
        
        # Pattern 2: Value with unit and flag
        value_match = re.search(r'([0-9,\.]+)\s*([A-Za-z\*\^0-9\/\%]+)?\s*(Bas|Élevé|Low|High)?', line)
        if value_match and 'Valeur de référence' not in line:
            try:
                value_str = value_match.group(1).replace(',', '.')
                value = float(value_str)
                unit = value_match.group(2) or ''
                flag = value_match.group(3) or ''
                
                # Find the test name from context (this is simplified)
                # In a real implementation, you'd track the current test context
                return (None, value, unit, flag, '')
            except:
                pass
        
        # Pattern 3: Reference range
        ref_match = re.search(r'Valeur de référence\s*([0-9,\.\s\-\(\)A-Za-z\*\^\/\%]+)', line)
        if ref_match:
            ref_range = ref_match.group(1)
            return (None, None, None, None, ref_range)
        
        # Specific patterns for known tests
        test_patterns = {
            r'Leucocytes.*?([0-9,\.]+)\s*10\*9/L': ('Leucocytes', '10*9/L'),
            r'Hémoglobine.*?([0-9,\.]+)\s*g/L': ('Hémoglobine', 'g/L'),
            r'Hématocrite.*?([0-9,\.]+)(?:\s*Bas)?': ('Hématocrite', ''),
            r'Érythrocytes.*?([0-9,\.]+)\s*10\*12/L': ('Érythrocytes', '10*12/L'),
            r'Plaquettes.*?([0-9,\.]+)\s*10\*9/L': ('Plaquettes', '10*9/L'),
            r'Neutrophiles.*?([0-9,\.]+)\s*10\*9/L': ('Neutrophiles', '10*9/L'),
            r'NEUTROPHILES %.*?([0-9,\.]+)\s*%': ('NEUTROPHILES %', '%'),
            r'Lymphocytes.*?([0-9,\.]+)\s*10\*9/L': ('Lymphocytes', '10*9/L'),
            r'LYMPHOCYTES %.*?([0-9,\.]+)\s*%': ('LYMPHOCYTES %', '%'),
            r'Monocytes.*?([0-9,\.]+)\s*10\*9/L': ('Monocytes', '10*9/L'),
            r'MONOCYTES %.*?([0-9,\.]+)\s*%': ('MONOCYTES %', '%'),
            r'Éosinophiles.*?([0-9,\.]+)\s*10\*9/L': ('Éosinophiles', '10*9/L'),
            r'EOSINPHILE %.*?([0-9,\.]+)\s*%': ('EOSINPHILE %', '%'),
            r'Basophiles.*?([0-9,\.]+)\s*10\*9/L': ('Basophiles', '10*9/L'),
            r'BASOPHILES %.*?([0-9,\.]+)\s*%': ('BASOPHILES %', '%'),
        }
        
        for pattern, (test_name, unit) in test_patterns.items():
            match = re.search(pattern, line)
            if match:
                try:
                    value_str = match.group(1).replace(',', '.')
                    value = float(value_str)
                    flag = 'H' if 'Élevé' in line else 'L' if 'Bas' in line else ''
                    return (test_name, value, unit, flag, '')
                except:
                    continue
        
        return None
    
    def calculate_nlr(self, cbc_data: Dict) -> Optional[float]:
        """Calculate NLR if neutrophil and lymphocyte percentages are available"""
        if 'NEUT_PCT' in cbc_data and 'LYMPH_PCT' in cbc_data:
            neut_pct = cbc_data['NEUT_PCT']['value']
            lymph_pct = cbc_data['LYMPH_PCT']['value']
            if lymph_pct > 0:
                return round(neut_pct / lymph_pct, 2)
        return None
    
    def extract_from_pdf(self, file_path: str) -> Dict:
        """Main extraction method"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            format_type = self.detect_format(text)

            traditional_info = self.extract_patient_info_traditional(text)
            booklet_info = self.extract_patient_info_booklet(text)
            traditional_cbc = self.extract_cbc_traditional(text)
            booklet_cbc = self.extract_cbc_booklet(text)

            # Determine the most plausible extraction by comparing number of biomarkers captured
            if len(booklet_cbc) >= len(traditional_cbc) and len(booklet_cbc) > 0:
                chosen_format = 'quebec_health_booklet'
                patient_info = booklet_info or traditional_info
                cbc_data = booklet_cbc
            elif len(traditional_cbc) > 0:
                chosen_format = 'traditional_lab'
                patient_info = traditional_info or booklet_info
                cbc_data = traditional_cbc
            else:
                chosen_format = format_type
                patient_info = traditional_info or booklet_info
                cbc_data = {}

            result = {
                'patient_info': patient_info,
                'cbc_data': cbc_data,
                'additional_tests': {},
                'extraction_metadata': {
                    'format': chosen_format,
                    'source_file': file_path,
                    'extracted_at': datetime.now().isoformat(),
                    'success': False,
                    'cbc_tests_found': 0
                }
            }

            # Calculate NLR if possible
            nlr = self.calculate_nlr(result['cbc_data'])
            if nlr:
                result['cbc_data']['NLR'] = {
                    'value': nlr,
                    'unit': 'ratio',
                    'flag': '',
                    'reference_range': '1.0-3.0',
                    'original_name': 'Calculated NLR'
                }
            
            result['extraction_metadata']['success'] = len(result['cbc_data']) > 0
            result['extraction_metadata']['cbc_tests_found'] = len(result['cbc_data'])
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'extraction_metadata': {
                    'format': 'unknown',
                    'source_file': file_path,
                    'extracted_at': datetime.now().isoformat(),
                    'success': False,
                    'cbc_tests_found': 0
                }
            }

def test_universal_extractor():
    """Test the universal extractor on all CarnetSante files"""
    
    files = [
        "/Users/shayanhajhashemi/Documents/Rhizome/assets/carnetsante/carnetsante_sample_shayan_blood_test.pdf",
        "/Users/shayanhajhashemi/Documents/Rhizome/assets/carnetsante/ben_carnetsante_type2.pdf", 
        "/Users/shayanhajhashemi/Documents/Rhizome/assets/carnetsante/shayan_carnetsante_type2.pdf"
    ]
    
    extractor = UniversalCarnetSanteExtractor()
    
    for file_path in files:
        print(f"\n{'='*80}")
        print(f"TESTING: {Path(file_path).name}")
        print(f"{'='*80}")
        
        result = extractor.extract_from_pdf(file_path)
        
        print(f"Format: {result['extraction_metadata']['format']}")
        print(f"Success: {result['extraction_metadata']['success']}")
        print(f"CBC Tests Found: {result['extraction_metadata']['cbc_tests_found']}")
        
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

if __name__ == "__main__":
    test_universal_extractor()
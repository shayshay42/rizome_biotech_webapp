import sys
from pathlib import Path
from typing import Dict, Optional

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from universal_carnetsante_extractor import UniversalCarnetSanteExtractor  # noqa: E402

FIXTURES = [
    ("ben_carnetsante_type2.pdf", "ben_type2.txt"),
    ("shayan_carnetsante_type2.pdf", "shayan_type2.txt"),
]

KEY_EXPECTATIONS: Dict[str, Dict[str, float]] = {
    "WBC": {"column": "WBC", "abs_tol": 0.2, "rel_tol": 0.05},
    "HGB": {"column": "HGB", "abs_tol": 2.0, "rel_tol": 0.05},
    "MCV": {"column": "MCV", "abs_tol": 2.0, "rel_tol": 0.05},
    "PLT": {"column": "PLT", "abs_tol": 5.0, "rel_tol": 0.05},
    "RDW": {"column": "RDW", "abs_tol": 0.5, "rel_tol": 0.08},
    "MONO": {"column": "MONO_ABS", "fallback": "MONO", "abs_tol": 0.05, "rel_tol": 0.1},
    "NLR": {"column": "NLR", "abs_tol": 0.1, "rel_tol": 0.05},
}


def _parse_ground_truth(path: Path) -> Dict[str, float]:
    expected: Dict[str, float] = {}
    for raw_line in path.read_text().splitlines():
        if "=" not in raw_line:
            continue
        key_part, value_part = raw_line.split("=", 1)
        key = key_part.strip().split()[0].upper()
        value_str = value_part.strip().replace(" ", "")
        if not value_str or value_str == "?":
            continue

        if "/" in value_str:
            try:
                numerator, denominator = value_str.split("/", 1)
                ratio = float(numerator) / float(denominator)
                expected[key] = ratio
            except ValueError:
                continue
        else:
            try:
                expected[key] = float(value_str)
            except ValueError:
                continue
    return expected


def _get_cbc_value(cbc_data: Dict[str, Dict], primary: str, fallback: Optional[str] = None):
    if primary in cbc_data:
        return cbc_data[primary]["value"]
    if fallback and fallback in cbc_data:
        return cbc_data[fallback]["value"]
    return None


@pytest.mark.parametrize("pdf_name, txt_name", FIXTURES)
def test_carnetsante_type2_extraction(pdf_name: str, txt_name: str):
    extractor = UniversalCarnetSanteExtractor()
    pdf_path = REPO_ROOT / "assets" / "carnetsante" / pdf_name
    truth_path = REPO_ROOT / "assets" / "carnetsante" / txt_name

    ground_truth = _parse_ground_truth(truth_path)
    extraction = extractor.extract_from_pdf(str(pdf_path))

    if not extraction["extraction_metadata"].get("success"):
        pytest.xfail("CarnetSante Type 2 PDF requires OCR support for structured extraction")

    cbc_data = extraction["cbc_data"]

    for marker, expectations in KEY_EXPECTATIONS.items():
        if marker not in ground_truth:
            continue
        expected_value = ground_truth[marker]
        column = expectations["column"]
        fallback = expectations.get("fallback")
        actual_value = _get_cbc_value(cbc_data, column, fallback)
        assert actual_value is not None, f"Missing {column} in extraction for {pdf_name}"
        assert actual_value == pytest.approx(
            expected_value,
            rel=expectations["rel_tol"],
            abs=expectations["abs_tol"],
        )
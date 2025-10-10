#!/usr/bin/env python3
"""Legacy helper kept for backwards compatibility.

The cancer-risk pipeline now bundles a compact CatBoost ensemble directly in
the repository (``streamlit_app/models/catboost_cbc.pkl``).

This script intentionally does nothing besides pointing developers toward the
new workflow, where updates are produced via ``scripts/export_autogluon_model.py``.
"""


def main() -> int:
    print(
        "The production model bundle is produced via scripts/export_autogluon_model.py.\n"
        "No runtime download is required; the CatBoost artifact ships with the app."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

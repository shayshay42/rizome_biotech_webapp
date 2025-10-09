
# Rhizome CBC Analysis - Streamlit Web Application

This application is designed to complement the main Rhizome CBC analysis research platform and provides a user-friendly interface for the underlying machine learning capabilities.

## Cleaning the public repo

If markdown docs or test files were already pushed before we updated `.gitignore`, remove them from the remote history once:

```bash
git rm -r --cached *.md
git rm -r --cached test_*.py
git rm -r --cached tests
git add README.md
git commit -m "Prune docs and tests from deployment repo"
git push
```

After running these commands locally, the files disappear from GitHub but stay on your machine.

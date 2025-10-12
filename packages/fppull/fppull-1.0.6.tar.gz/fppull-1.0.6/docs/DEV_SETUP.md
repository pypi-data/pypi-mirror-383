# Developer Quickstart

## Environment setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install
```

## Local validation
Before pushing:
```bash
pre-commit run --all-files
make ci
```

## One-line reset
If your pre-commit hook breaks:
```bash
rm -rf ~/.cache/pre-commit && pre-commit clean && pre-commit install
```

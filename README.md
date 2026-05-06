# CodeShield 🛡️

A Technical Debt and Security Scanner for Python source code, developed for DevMetrics PLC as part of the CI6125 Software Development Practice module at Kingston University.

The tool scans `.py` files and combines cyclomatic complexity with security red flag detection to produce a Technical Debt Index (TDI), giving developers and managers a clearer picture of which parts of a codebase need attention first.

---

## What it does

- Counts effective lines of code (blank lines and comments excluded)
- Calculates cyclomatic complexity per function
- Detects security red flags:
  - Hardcoded credentials (passwords, tokens, API keys)
  - Weak cryptographic algorithms (`hashlib.md5`, `hashlib.sha1`)
  - SQL injection patterns (string concatenation in `execute()`)
  - Commented-out code blocks (3+ consecutive lines)
- Calculates vulnerability density (red flags per 1,000 LoC)
- Combines everything into a TDI score with a Low / Medium / High risk label
- Flags any function or file that exceeds TDI ≥ 50 with a critical alert
- Keeps a scan history for the current browser session
- Handles invalid Python files with an inline error message

---

## Stack

| | |
|---|---|
| Backend | Python, Flask |
| Scanner | Python `ast` module |
| Frontend | HTML, CSS, JavaScript |
| Storage | Browser `sessionStorage` |

---

## Project structure

```
codeshield/
├── app.py              # entry point
├── views.py            # routes (/scan, /scanResult, /scanHistory)
├── tdiScanner.py       # scanner engine
├── tests.py            # unit tests
├── static/
│   ├── css/
│   ├── js/
│   └── icons/
└── templates/
    ├── home.html
    ├── scanResult.html
    └── scanHistory.html
```

---

## Setup

Requires Python 3.8+.

```bash
git clone https://github.com/badarianof/codeshield.git
cd codeshield
pip install flask
python app.py
```

Then open `http://localhost:8000` in your browser.

---

## Tests

```bash
pip install pytest
pytest tests.py -v
```

Covers LoC counting, complexity calculation, vulnerability density, the TDI formula, risk classification, and all five red flag categories.

---

## TDI formula

```
TDI = (Complexity × 0.5) + (Vulnerability Density × 0.5)
```

| TDI | Risk |
|---|---|
| 0 – 19 | Low |
| 20 – 49 | Medium |
| 50+ | High — immediate refactoring recommended |

---

## Limitations

- Only python files can be scanned
- Complexity uses the decision-point approximation (`M = 1 + decision points`), equivalent to `M = E − N + 2P` for a single connected function
- Red flag detection is pattern-based — findings should always be reviewed manually before acting on them
- Scan history is session-based and clears when the browser closes
- This is a prototype, not a production security tool

---

## Team

JAMMS FABS — Badaria Gafoor, Sina Gurung, Suprina Gurung, Fatima Khan Khan, Joshua Kofi, Merrone Melaku, Mijash Thapa, Aamiin Wanis

---

## License

[MIT](LICENSE)

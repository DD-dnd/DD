# Single EXE sizing calculator

This repository now includes a single-file Python calculator (`calculator.py`) for:
- Rectifiers
- 1PH battery chargers
- 3PH battery chargers

## Run
```bash
python calculator.py rectifier --vdc 600 --idc 600 --vpri 480 --json
```

## Tests
```bash
python -m unittest -v
```

## Build one-file executable
```bash
pyinstaller --onefile calculator.py
```

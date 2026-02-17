# Single EXE sizing calculator

This repository includes a single-file Python calculator (`calculator.py`) for:
- Rectifiers
- 1PH battery chargers
- 3PH battery chargers

## How to run the local Python file

### 1) Check Python is installed
```bash
python --version
```
(Use `python3 --version` if your system uses `python3`.)

### 2) Run the calculator directly
From this folder (`/workspace/DD`):
```bash
python calculator.py rectifier --vdc 600 --idc 600 --vpri 480 --json
```

Other examples:
```bash
python calculator.py 1ph --vdc 125 --idc 50 --vpri 240 --json
python calculator.py 3ph --vdc 600 --idc 400 --vpri 480 --json
```

### 3) Interactive mode (no arguments)
If you run without arguments, the tool now prompts for Family, Vdc, Idc, Vpri:
```bash
python calculator.py
```

### 4) Run tests
```bash
python -m unittest -v
```

## Build one-file executable
```bash
pyinstaller --onefile calculator.py
```

Run with arguments:
```bash
./dist/calculator rectifier --vdc 600 --idc 600 --vpri 480 --json
```

Or start interactive mode with no arguments:
```bash
./dist/calculator
```

(On Windows use `dist\\calculator.exe ...` or `dist\\calculator.exe` for interactive mode.)

# ImgTrimmer

This app runs locally and helps you crop experimental results to easily create publication-ready figures.

## Installation

```
git clone https://github.com/astaka-pe/ImgTrimmer.git
cd ImgTrimmer

# Linux
python3 -m venv .venv
source .venv/bin/activate # source .venv/bin/activate.fish

# Windows
py -3.10 -m venv .venv
.venv/Scripts/activate

pip install -r requirements.txt
```

## Demo

```
streamlit run app.py
```

![Image](docs/demo.gif)

## Todo

- [ ] Operation check on Linux
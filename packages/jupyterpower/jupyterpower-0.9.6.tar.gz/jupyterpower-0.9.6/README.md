# JupyterPower

This is a Python API for use in Data Science with Jupyter Notebooks for end-to-end ML Engineering, MLOps, Data Science productions tasks

## Devlopment
`python -m venv .venv`

`source .venv/bin/activate # Windows: .venv\\Scripts\\activate`

`pip install -r requirements.txt`

## How to View vs Re-Run

### View only (no setup required)
- Open `YOUR_NOTEBOOK.ipynb` in VS Code, JupyterLab, or GitHub’s viewer.
- The notebook is saved **with outputs embedded**, so plots and tables should appear immediately.
- If VS Code shows a trust prompt, choose **Trust** for this workspace.

### Re-run the notebook

From repo root
`python -m venv .venv && source .venv/bin/activate`  

`python -m pip install --upgrade pip`

`python -m pip install -r requirements.txt`

`code .`  # open VS Code here (or use JupyterLab)

The `requirements.lock.baseline.txt` file was created using: 

`pip freeze > requirements.lock.baseline.txt`

To restore or setup a new .venv in VS Code, run this:

`python -m pip install -r requirements.lock.baseline.txt`

# Release Process — jupyterpower (import: jupyterpower)

1. Bump version (both places)
- `src/jupyterpower/_version.py` → `__version__ = "0.9.x"`
- `pyproject.toml` → `[project].version = "0.9.x"`

2. Test locally
```bash
./.venv/bin/python -m pytest -q

3. Commit and Push
git add -A
git commit -m "chore(release): v0.9.x"
git push


4. Clean Build
rm -rf dist build *.egg-info
./.venv/bin/python -m pip install --upgrade build twine
./.venv/bin/python -m build
./.venv/bin/python -m twine check dist/*

5. Dry Run
export TEST_PYPI_TOKEN='pypi-xxxxxxxx'
./.venv/bin/python -m twine upload -r testpypi -u __token__ -p "$TEST_PYPI_TOKEN" dist/*
# Verify in a fresh env:
python3 -m venv /tmp/jp-test && source /tmp/jp-test/bin/activate
python -m pip install --upgrade pip
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ jupyterpower==0.1.x
deactivate

6. Publish PyPi
export PYPI_TOKEN='pypi-xxxxxxxx'
./.venv/bin/python -m twine upload -u __token__ -p "$PYPI_TOKEN" dist/*

7. Tag the release in GitHub
git tag v0.1.x && git push origin v0.1.x



## Install
From PyPI:
```bash
pip install jupyterpower

## Check install
python -c "import jupyterpower; print(jupyterpower.__version__)"

## Load a CSV, smooth a column, fit a simple baseline, and save a plot:
from jupyterpower import DATA_DIR, RESULTS_DIR, load_csv, moving_average, fit_linear_time
from jupyterpower.viz import plot_series_with_smooth, save_fig

# explicit columns for this demo schema
time_col  = "time"
value_col = "signal"

df = load_csv(DATA_DIR / "sample.csv", create_placeholder=True)
smooth = moving_average(df, value_col=value_col, window=7)
model, X, y, pred = fit_linear_time(df, time_col=time_col, y_col=value_col)

fig, ax = plot_series_with_smooth(df, time_col=time_col, value_col=value_col, smooth=smooth)
out_png = RESULTS_DIR / "quickstart_plot.png"
save_fig(fig, out_png)
print("Saved:", out_png)



## Using a Jupyter Notebook
%load_ext autoreload
%autoreload 2
import jupyterpower; print("jupyterpower", jupyterpower.__version__)


## Development (editable install)
If you’re working from a cloned repo:

python -m pip install -e .
python -m pip install pytest
pytest -q


## Uninstall any old packages

### Make sure your project .venv is active:
`source .venv/bin/activate`

### Uninstall any old bits (jupyterpower & jpower), and show leftovers

```
# sanity
which python
python -m pip --version

# uninstall both names (safe even if not present)
python -m pip uninstall -y jupyterpower jpower

# look for any stragglers in site-packages (dry run list)
python - <<'PY'
import sys, sysconfig, pathlib
sp = pathlib.Path(sysconfig.get_paths()["purelib"])
candidates = [p for p in sp.iterdir() if p.name.lower().startswith(("jpower","jupyterpower"))]
print("Site-packages:", sp)
print("Leftovers:", [p.name for p in candidates] or "None")
PY
```

### Install the newest from PyPI (clean)

`python -m pip install --upgrade --no-cache-dir jupyterpower`

### Verify jupyterpower is installed

```
# package metadata
python -m pip show jupyterpower

# freeze view (should show jupyterpower==0.9.5, and NOT jpower)
python -m pip freeze | egrep -i '^(jupyterpower|jpower)'

# python-level verification (import + dist check + scan site-packages)
python - <<'PY'
import sys, importlib, importlib.metadata as md, sysconfig, pathlib
print("PY:", sys.executable)
# import should succeed
m = importlib.import_module("jupyterpower")
print("✅ import jupyterpower OK")
print("CODE version:", getattr(m, "__version__", "unknown"))
print("CODE file   :", getattr(m, "__file__", "unknown"))
# distribution metadata
print("DIST version:", md.version("jupyterpower"))
# ensure no 'jpower' dist present
bad = [d for d in md.distributions() if d.metadata["Name"].lower()=="jpower"]
print("Other dist named 'jpower':", [b.metadata["Version"] for b in bad] or "None")
# scan site-packages for any top-level jpower folders
sp = pathlib.Path(sysconfig.get_paths()["purelib"])
leftovers = [p.name for p in sp.iterdir() if p.name.lower().startswith("jpower")]
print("Site-packages leftovers starting with 'jpower':", leftovers or "None")
PY
```


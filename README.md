# Cropland-Driven Deforestation Analysis

### 🎯 Goals

1. Download data using Google Earch Engine
2. Analyze data for multiple datasets

### 🛠️ Tools

* [Google Earch Engine - GEE](https://code.earthengine.google.com/)
* Python spatial frameworks (geopandas, shapely, etc.)
* [UV](https://github.com/astral-sh): Python project management
    * Ultrafast, state-of-the-art, Python project manager
    * Instigate us to follow best coding practices
    * Easy-to-use

## Project Setup

### Python Environment

Clone the repository and enter the project folder:

```bash
git clone https://github.com/cmcouto-silva/cropland-driven-deforestation.gitgit && \
cd cropland-driven-deforestation
``` 


Install [UV](https://github.com/astral-sh) and create the environment with uv sync.


```bash
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows.
# powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Install the required Python version and all required dependencies by running:

```
uv sync
```

[Optional] If using GEE Python API:

```bash
# Set up your personal token
uv run scripts/set_gee.py
```

### Download data

Two options: 
1. Use the scripts from `scripts/js` on GEE Web UI (preferable)
2. Run export_dataset.py with `uv run scripts/export_datasets.py` (missing implementing the crop data export).

The config for downloading these data can be found under `configs/config.yaml`.

### Analysis

For the analysis, we used the data called `br_deforestation_biome.geojson`, provided for our task. The notebook with the analysis can be found under `notebooks/eda.ipynb`. Figures available on `reports/figures`.

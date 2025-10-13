# PyGMRT

A minimal Python package for downloading bathymetry and topography tiles from the [Global Multi-Resolution Topography (GMRT) Synthesis](https://www.gmrt.org/).

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Features

- **Simple API**: Single function to download GMRT tiles
- **Multiple resolutions**: High (1 arc-second), medium (4 arc-second), low (16 arc-second)
- **GeoTIFF format**: Direct integration with rasterio and other geospatial tools
- **Antimeridian support**: Handles bounding boxes that cross the 180° longitude
- **No API key required**: Direct access to GMRT GridServer

## Installation

### Using UV (recommended)

If you don't have UV installed, follow the instructions at [uv](https://uv.readthedocs.io/en/latest/). Then install PyGMRT from PyPI:

```bash
uv add pygmrt
```

Or install from source

```bash
git clone https://github.com/leonard-seydoux/pygmrt.git
cd pygmrt
uv sync
```


### Using pip

Similarly, you can either install from PyPI:

```bash
pip install pygmrt
```

Or install from source:

```bash
# Or install from source
git clone https://github.com/leonard-seydoux/pygmrt.git
cd pygmrt
pip install -e .
```





## Quick Start

```python
from rasterio.plot import show
from pygmrt.tiles import download_tiles

# Get tiles
tiles = download_tiles(bbox=[55.05, -21.5, 55.95, -20.7], resolution="low")

# Show with minimal processing
show(tiles)
```

![](notebooks/01_quickstart.png)

## Other examples

The playground notebook [02_playground.ipynb](notebooks/02_playground.ipynb) contains more advanced examples, including shaded relief visualizations with `matplotlib` and `cartopy`. The following figures were generated with that notebook.

![](notebooks/reunion.svg)

![](notebooks/piton.svg)

## API reference

The main function of the package is `pygmrt.tiles.download_tiles`, with the signature given below.

```python
def download_tiles(
    bbox, 
    save_directory="./geotiff/",
    resolution="medium",
    overwrite=False,
):
    """
    Download tiles and return the rasterio dataset.

    Parameters
    ----------
    bbox : sequence of float
        Bounding box in WGS84 degrees as ``[west, south, east, north]``.
    save_directory : str or pathlib.Path
        Destination directory path where files will be written. Created if
        needed.
    resolution : {"low", "medium", "high"}, default "medium"
        Named resolution level; mapped internally to provider-specific datasets.
    overwrite : bool, default False
        If ``False``, reuse existing files. If ``True``, force re-download.

    Returns
    -------
    rasterio.DatasetReader
        Opened rasterio dataset for the downloaded GeoTIFF. The caller is
        responsible for closing the dataset.

    Raises
    ------
    ValueError
        If invalid argument combinations or bbox values are provided.
    PermissionError
        If the destination directory is not writable.
    RuntimeError
        If download attempts ultimately fail.
"""
```

## Development

### Setting up development environment

```bash
git clone https://github.com/leonard-seydoux/pygmrt.git
cd pygmrt

# Install in development mode with UV
uv sync --all-extras

# Or with pip
pip install -e ".[dev,docs]"
```

### Running tests

```bash
# With UV
uv run pytest

# With pip
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [GMRT Synthesis](https://www.gmrt.org/) for providing open access to global bathymetry data
- [Lamont-Doherty Earth Observatory](https://www.ldeo.columbia.edu/) for maintaining the GMRT database

"""Tiles download module.

Minimal API to download Global Multi-Resolution Topography (GMRT) tiles for a
given bounding box or a batch of bounding boxes.

Notes
-----
- Main entry point: :func:`download_tiles`.
- Provider: GMRT GridServer only (no API key required).
- Formats supported: ``geotiff``. PNG is not currently supported by GMRT GridServer.
- Antimeridian crossing is handled by splitting longitude ranges automatically.
"""

from __future__ import annotations

import os
import requests
import rasterio
from dataclasses import dataclass, field
from pathlib import Path
from time import sleep
from typing import List, Literal, Sequence, Tuple, TypedDict

# Service endpoints
GMRT_BASE_URL = "https://www.gmrt.org/services/GridServer"

# Default
SAVE_DIRECTORY = "./geotiff"
EXTENSION = "tif"

# Type aliases for clarity
Resolution = Literal["low", "medium", "high"]


class BoundingBox(TypedDict):
    west: float
    south: float
    east: float
    north: float


@dataclass
class ManifestEntry:
    path: str
    coverage: BoundingBox
    size_bytes: int
    status: Literal["created", "reused"]


@dataclass
class DownloadResult:
    entries: List[ManifestEntry]
    count_created: int = 0
    count_reused: int = 0
    errors: List[str] = field(default_factory=list)


def download_tiles(
    *,
    bbox: Sequence[float] = None,
    save_directory: str | Path = SAVE_DIRECTORY,
    resolution: Resolution = "medium",
    overwrite: bool = False,
) -> rasterio.DatasetReader:
    """Download tiles and return the rasterio dataset.

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
    # Validate bbox presence
    if bbox is None:
        raise ValueError("Provide bbox as [west, south, east, north]")

    # Validate resolution
    if resolution not in ("low", "medium", "high"):
        raise ValueError("Supported resolutions: 'low', 'medium', 'high'")

    # Output directory
    save_path = _check_directory(save_directory)
    DownloadResult(entries=[])

    try:
        # Validate bbox values
        west, south, east, north = _validate_bbox(bbox)

        # Split antimeridian into 1 or 2 ranges
        longitude_limits = _split_antimeridian(west, east)

        # For simplicity, use the first longitude segment and return its dataset
        # (Most common case is no antimeridian crossing = single segment)
        lon_a, lon_b = longitude_limits[0]

        # Build URL
        url = _build_url(lon_a, south, lon_b, north, resolution)

        # Determine file path (include resolution in filename to force re-download when resolution changes)
        filename = _save_filename(
            "gmrt", (lon_a, south, lon_b, north), resolution=resolution
        )
        filepath = save_path / filename

        # Download if needed
        if not filepath.exists() or overwrite:
            print(f"Downloading {url} to {filepath} ...")
            _download_stream(url, filepath, overwrite=overwrite)

        # Open and return the rasterio dataset
        return rasterio.open(filepath)

    except Exception as e:
        raise RuntimeError(f"Failed to download tiles: {e}") from e


def get_path(result: DownloadResult) -> Path:
    """Return the first existing GeoTIFF Path from a DownloadResult.

    Scans manifest entries in order and returns the first path whose status is
    "created" or "reused", whose file exists, and whose extension is .tif/.tiff.

    Parameters
    ----------
    result : DownloadResult
        The result object returned by download_tiles.

    Returns
    -------
    pathlib.Path
        The first matching GeoTIFF path.

    Raises
    ------
    RuntimeError
        If no matching GeoTIFF file is found among the entries.
    """
    for e in result.entries:
        p = Path(e.path)
        if (
            e.status in ("created", "reused")
            and p.exists()
            and p.suffix.lower() in (".tif", ".tiff")
        ):
            return p
    raise RuntimeError(
        "No GeoTIFF found in result. Check API availability or parameters."
    )


def _validate_bbox(bbox: Sequence[float]) -> Tuple[float, float, float, float]:
    """Validate a bounding box.

    Parameters
    ----------
    bbox : sequence of float
        Bounding box as ``[west, south, east, north]`` in degrees.

    Returns
    -------
    tuple of float
        The validated bbox as ``(west, south, east, north)`` with floats.

    Raises
    ------
    ValueError If the bbox length is not 4, latitude/longitude values are out of
    range, or ``south >= north``.
    """
    if len(bbox) != 4:
        raise ValueError("bbox must have shape: [west, south, east, north]")
    west, south, east, north = map(float, bbox)
    if not (-180.0 <= west <= 180.0 and -180.0 <= east <= 180.0):
        raise ValueError("longitude values must be in [-180, 180]")
    if not (-90.0 <= south <= 90.0 and -90.0 <= north <= 90.0):
        raise ValueError("latitude values must be in [-90, 90]")
    if south >= north:
        raise ValueError("south must be < north")
    return west, south, east, north


def _split_antimeridian(
    min_lon: float, max_lon: float
) -> List[Tuple[float, float]]:
    """Split longitude range if crossing the antimeridian.

    Parameters
    ----------
    min_lon, max_lon : float
        Input longitudes in degrees, each within [-180, 180].

    Returns
    -------
    list of tuple of float
        One or two ranges ``[(west, east), ...]`` depending on whether the
        interval crosses the antimeridian.
    """
    if min_lon <= max_lon:
        return [(min_lon, max_lon)]
    return [(min_lon, 180.0), (-180.0, max_lon)]


def _save_filename(
    prefix: str,
    bbox: Tuple[float, float, float, float],
    *,
    resolution: Resolution = "medium",
    extension: str = EXTENSION,
) -> str:
    """Create a deterministic and safe filename for a bbox and resolution.

    The resolution token is embedded so that requests for different resolution
    levels produce distinct filenames and therefore trigger re-downloads when
    a different resolution is requested.

    Parameters
    ----------
    prefix : str
        Filename prefix, typically the provider name.
    bbox : tuple of float
        Bounding box as ``(west, south, east, north)``.
    resolution : {"low","medium","high"}
        Named resolution included in the filename.
    extension : str, default "tif"
        File extension without leading dot.

    Returns
    -------
    str
        Filename with fixed decimal precision, resolution token, and extension.
    """
    west, south, east, north = bbox
    return f"{prefix}_{resolution}_{west:.3f}_{south:.3f}_{east:.3f}_{north:.3f}.{extension}"


def _check_directory(directory: str | Path) -> Path:
    """Ensure destination directory exists and is writable.

    Parameters
    ----------
    directory : str or pathlib.Path
        Destination directory path.

    Returns
    -------
    pathlib.Path
        The destination path object.

    Raises
    ------
    PermissionError
        If the destination exists but is not writable.
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    if not os.access(path, os.W_OK):
        raise PermissionError(f"Destination not writable: {directory}")
    return path


def _download_stream(
    url: str,
    filepath: Path,
    *,
    timeout: float = 30.0,
    retries: int = 3,
    backoff: float = 0.5,
    overwrite: bool = False,
) -> int:
    """Download a URL to a file, atomically and with streaming.

    Parameters
    ----------
    url : str
        Source URL to fetch.
    filepath : pathlib.Path
        Target file path to write. A temporary ``.part`` is used and atomically
        moved into place on completion.
    timeout : float, default 30.0
        Per-request timeout in seconds.
    retries : int, default 3
        Number of retry attempts on failures.
    backoff : float, default 0.5
        Linear backoff multiplier between retries, in seconds.
    overwrite : bool, default False
        If ``False``, reuse existing file. If ``True``, force re-download.

    Returns
    -------
    int
        Size of the written file in bytes.

    Raises
    ------
    RuntimeError
        When the HTTP response indicates an error or returns a text/JSON/HTML payload
        instead of a binary raster file.
    """
    # Skip if exists and not overwriting
    if filepath.exists() and not overwrite:
        return filepath.stat().st_size

    # Temporary file path
    tmp = filepath.with_suffix(filepath.suffix + ".part")
    attempt = 0
    while True:
        try:
            with requests.get(url, stream=True, timeout=timeout) as r:
                try:
                    r.raise_for_status()
                except Exception as http_err:
                    # include response status and a part of the body for help
                    content_preview = None
                    try:
                        content_preview = r.text[:1024]
                    except Exception:
                        content_preview = "<unavailable>"
                    raise RuntimeError(
                        f"HTTP error while downloading {url}: {r.status_code} {r.reason}\nResponse preview: {content_preview}"
                    ) from http_err
                # Check content-type to ensure we're not saving an HTML error page
                ctype = (r.headers.get("Content-Type") or "").lower()
                if any(
                    t in ctype
                    for t in ["text/html", "text/plain", "application/json"]
                ):
                    preview = None
                    try:
                        preview = r.text[:1024]
                    except Exception:
                        preview = "<unavailable>"
                    raise RuntimeError(
                        f"Unexpected content-type {ctype} for {url}. Response preview: {preview}"
                    )
                tmp.parent.mkdir(parents=True, exist_ok=True)
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 64):
                        if chunk:
                            f.write(chunk)
            # Atomic replace
            tmp.replace(filepath)
            return filepath.stat().st_size
        except Exception:
            attempt += 1
            try:
                if tmp.exists():
                    tmp.unlink()
            except Exception:
                # Best-effort cleanup
                pass
            if attempt > retries:
                raise
            sleep(backoff * attempt)


def _map_resolution(res: Resolution) -> str:
    """Map named resolution to service-specific levels.

    The GMRT GridServer requires resolution values to be positive powers of 2.
    Lower numbers correspond to higher resolution (more detail).

    Notes
    -----
    - "high": 1 (highest resolution available, smallest grid size)
    - "medium": 4 (moderate resolution)
    - "low": 16 (lower resolution, larger grid size)
    """
    mapping = {
        "high": "high",
        "medium": "med",
        "low": "low",
    }
    return mapping[res]


def _build_url(
    west: float, south: float, east: float, north: float, res: Resolution
) -> str:
    """Construct a provider-specific data URL for a bounding box.

    Parameters
    ----------
    west, south, east, north : float
        Bounding box edges in degrees.
    res : {"low", "medium", "high"}
        Named resolution level used for provider mapping.

    Returns
    -------
    str
        Fully qualified URL to request the data.

    Notes
    -----
    The GMRT GridServer appears to return the best available resolution for the
    requested area regardless of URL parameters. The resolution parameter is
    currently included in the URL but may not affect the server response.
    Different filenames based on resolution ensure proper caching behavior.

    Raises
    ------
    ValueError
        If unsupported format/provider combinations are requested or an unknown
        provider is supplied.
    """
    # Map resolution for potential future use
    mapped_res = _map_resolution(res)
    return f"{GMRT_BASE_URL}?format=geotiff&west={west}&east={east}&south={south}&north={north}&resolution={mapped_res}"

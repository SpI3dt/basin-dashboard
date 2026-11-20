# Basin Morphometrics Dashboard

An interactive dashboard that maps morphometric parameters for drainage basins in northern West Bengal (Himalayan foothills and adjoining plains, roughly 88.3°E to 88.9°E and 26.5°N to 27.2°N). The parameters are computed from an ASTER DEM and follow ideas from Ghosh & Sivakumar (2018) on morphometric indicators of active tectonics.

**Live app:** <paste your streamlit.app link here>

## What it shows

- Maps of five parameters per basin, either all together or one at a time
- A basin inspector: pick a basin to highlight it on the map and compare its value with every other basin
- A table of all basin values, with CSV download

## Parameters

| Code | Parameter | Formula | High value suggests |
|---|---|---|---|
| HI | Hypsometric integral | (E_mean − E_min) / (E_max − E_min) | Young, uplifted landscape |
| RR | Relief ratio | (E_max − E_min) / L_b | Steeper basin |
| DD | Drainage density | total stream length / basin area (km/km²) | More dissected terrain |
| RI | Ruggedness index | (E_max − E_min) × DD / 1000 | Rougher relief |
| BC | Basin compactness | 4πA / P² | Closer to circular (low = elongated) |

E = elevation in metres, L_b = longest basin length, A = basin area, P = basin perimeter.

## How the data was made

1. **DEM:** ASTER Global DEM V003 (30 m resolution) from NASA Earthdata, tiles: <list the tile names you used>.
2. **Hydrology (WhiteboxTools):** fill depressions, D8 flow direction, flow accumulation, stream extraction (threshold 90,000 cells), sub-basin delineation.
3. **Statistics:** minimum, maximum and mean elevation per basin from the DEM (rasterstats). Lengths, areas and perimeters are measured in UTM zone 45N (EPSG:32645).
4. **Display:** Streamlit, geopandas and matplotlib.

The analysis script is not part of this repo. This repo holds only the dashboard and the saved results.

## Run locally

```
pip install -r requirements.txt
streamlit run map_dashboard.py
```

## Files

- `map_dashboard.py`: the Streamlit app
- `basins_morphometrics.geojson`: basin polygons with the computed parameters
- `requirements.txt`: Python dependencies

## Limitations

- Basins come from a flow-accumulation threshold I chose, so basin size and count depend on that choice.
- Basins cut off by the edge of the DEM window are partial, so their values are less reliable.
- Drainage density is measured from the same stream network used to split the basins. It is therefore low compared with the paper's values and depends on the threshold. Ruggedness is built on drainage density and inherits this.
- The hypsometric integral is noisy in flat, low-relief basins on the plains, so read it together with the relief ratio.
- Basin compactness uses 4πA/P², which differs from the formula printed in the paper. Raster-derived outlines are jagged, which inflates the perimeter and lowers the values, so compare basins with each other rather than with published numbers.
- Values will not match the paper exactly (different region, basins, DEM processing and tools).
- These are relative morphometric indicators. They do not predict earthquakes.

## Reference

Ghosh, S., & Sivakumar, R. (2018). Assessment of morphometric parameters for the development of Relative Active Tectonic Index and its significant for seismic hazard study: an integrated geoinformatic approach. *Environmental Earth Sciences*, 77, 600. https://doi.org/10.1007/s12665-018-7787-6

## Authors

<Siddharth. B, Niranjan C.I>, <SRMIST>

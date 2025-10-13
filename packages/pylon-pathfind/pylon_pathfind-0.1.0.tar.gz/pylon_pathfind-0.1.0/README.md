# pylon_pathfind

A lightweight, **weather-aware** pathfinding library designed for the IoT‑Powered Mobile Weather Observation Station project.
It provides a clean API to compute shortest paths under dynamic penalties (e.g., rain, fog), and is ready to integrate on a Raspberry Pi.

## Install (local)

```bash
pip install .   # from the project root (the folder with pyproject.toml)
# or
pip install /path/to/pylon_pathfind-0.1.0-py3-none-any.whl
```

## Usage

```python
from pylon_pathfind import PathFinder, WeatherPenalties

pf = PathFinder()

# (optional) replace default penalties
pf.set_weather_penalties(WeatherPenalties(clear=1.0, rain=1.2, heavy_rain=1.8, fog=1.4))

# Load edges (name, name, distance_km)
edges = [
    ("Winterveld", "Reefentse", 24.0),
    ("Reefentse", "Temba", 12.0),
    ("Temba", "Klipdrift", 16.0),
    ("Temba", "Marokoleng", 7.3),
]
pf.load_edges(edges)

# Mark weather on a specific road (u->v)
pf.set_edge_condition(("Temba", "Klipdrift"), "rain")

# Compute best route (returns node_names_path, total_cost)
path_names, total = pf.find_path("Winterveld", "Marokoleng")
print(path_names, total)
```

## Key Concepts
- **Graph by names**: You can work entirely with human‑readable names (no indices necessary).
- **Weather conditions**: Attach a condition per directed edge; weights are multiplied by a penalty.
- **Pluggable algorithm**: Uses Dijkstra by default (suitable for non-negative weights).

## Raspberry Pi integration tips
- The package depends only on `networkx`. It runs fine on Raspberry Pi OS (Python ≥ 3.9).
- Keep the graph small and preloaded in JSON to avoid runtime parsing overhead.
- For live weather, map your sensor stream (BME280, Anemometer, GPS) to `set_edge_condition()` calls before computing routes.

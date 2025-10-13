try:
    # Prefer installed package import (normal case)
    from pylon_pathfind import PathFinder, WeatherPenalties
except Exception:
    # When running the example from the source tree (not installed), make
    # the project root importable so `from pylon_pathfind import ...` works.
    import sys, pathlib, os
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from pylon_pathfind import PathFinder, WeatherPenalties

import json, pathlib

def main():
    pf = PathFinder()
    demo = pathlib.Path(__file__).with_name("data").joinpath("demo_gauteng.json")
    pf.load_from_json(str(demo))
    pf.set_weather_penalties(WeatherPenalties(clear=1.0, rain=1.2, heavy_rain=1.8, fog=1.4))
    pf.set_edge_condition(("Temba","Klipdrift"), "rain")
    path, total = pf.find_path("Winterveld", "Marokoleng")
    print("Best path:", " -> ".join(path))
    print("Total cost:", round(total, 2))

if __name__ == "__main__":
    main()

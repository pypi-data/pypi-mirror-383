from dataclasses import dataclass, asdict
from typing import Dict, Tuple, Iterable, List
import networkx as nx

@dataclass
class WeatherPenalties:
    clear: float = 1.0
    rain: float = 1.2
    heavy_rain: float = 1.8
    fog: float = 1.4

class PathFinder:
    def __init__(self):
        self.G = nx.DiGraph()
        self._penalties = WeatherPenalties()
        # edge -> condition str (u_name, v_name)
        self._edge_conditions: Dict[Tuple[str, str], str] = {}

    # ---- Configuration ----
    def set_weather_penalties(self, penalties: WeatherPenalties):
        self._penalties = penalties

    # ---- Graph loading ----
    def load_edges(self, edges: Iterable[Tuple[str, str, float]]):
        """Add/replace edges defined as (u_name, v_name, base_weight).
        Idempotent: re-adding updates the weight.
        """
        for u, v, w in edges:
            if w < 0:
                raise ValueError(f"Edge weight must be non-negative: {(u,v,w)}")
            self.G.add_edge(u, v, base=float(w))

    def load_from_json(self, path: str):
        """Load a graph from a JSON structure: {"edges": [[u, v, weight], ...]}"""
        import json
        with open(path, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        edges = payload.get("edges", [])
        self.load_edges(edges)

    # ---- Weather ----
    def set_edge_condition(self, edge: Tuple[str, str], condition: str):
        """Set weather condition for a directed edge (u_name, v_name)."""
        u, v = edge
        if not self.G.has_edge(u, v):
            raise KeyError(f"Edge does not exist: {edge}")
        self._edge_conditions[(u, v)] = condition

    def clear_edge_condition(self, edge: Tuple[str, str]):
        self._edge_conditions.pop(edge, None)

    def reset_conditions(self):
        self._edge_conditions.clear()

    # ---- Pathfinding ----
    def _effective_weight(self, u: str, v: str) -> float:
        base = self.G.edges[u, v]["base"]
        cond = self._edge_conditions.get((u, v), "clear")
        factor = getattr(self._penalties, cond, 1.0)
        return base * float(factor)

    def find_path(self, start: str, end: str) -> Tuple[List[str], float]:
        """Compute a shortest path from start to end using Dijkstra on effective weights.
        Returns (path_names, total_weight). Raises networkx exceptions if unreachable.
        """
        # Build a dynamic weight function
        def weight_fn(u, v, d):
            return self._effective_weight(u, v)

        path = nx.shortest_path(self.G, source=start, target=end, weight=weight_fn, method='dijkstra')
        total = 0.0
        for i in range(len(path)-1):
            total += self._effective_weight(path[i], path[i+1])
        return path, total

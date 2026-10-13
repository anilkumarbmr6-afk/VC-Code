from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np


Point = Tuple[float, float]


def parse_tsp(path: str | Path) -> np.ndarray:
    """Parse a TSPLIB node coordinate file."""
    coords: Dict[int, Point] = {}
    filepath = Path(path)
    with filepath.open("r", encoding="utf-8") as handle:
        lines = handle.read().splitlines()

    in_section = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("NODE_COORD_SECTION"):
            in_section = True
            continue
        if stripped.startswith("EOF"):
            break
        if not in_section:
            continue
        pieces = stripped.split()
        if len(pieces) < 3:
            continue
        index = int(pieces[0])
        x = float(pieces[1])
        y = float(pieces[2])
        coords[index] = (x, y)

    if not coords:
        raise ValueError(f"Could not parse any city coordinates from {filepath}")

    ordered = np.array([coords[i] for i in sorted(coords)], dtype=float)
    return ordered


def euclidean_distance(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def build_distance_matrix(coords: np.ndarray) -> np.ndarray:
    differences = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]
    return np.sqrt(np.sum(differences * differences, axis=2))


def tour_length(route: Iterable[int], dist: np.ndarray) -> float:
    route_list = list(route)
    if not route_list:
        return 0.0
    total = 0.0
    n = len(route_list)
    for i in range(n):
        a = route_list[i]
        b = route_list[(i + 1) % n]
        total += dist[a, b]
    return total


def nearest_neighbor_start(start_idx: int, dist: np.ndarray) -> List[int]:
    n = len(dist)
    route = [start_idx]
    visited = {start_idx}
    current = start_idx

    while len(route) < n:
        nearest = None
        nearest_distance = math.inf
        for city in range(n):
            if city in visited:
                continue
            candidate = dist[current, city]
            if candidate < nearest_distance:
                nearest_distance = candidate
                nearest = city
        if nearest is None:
            break
        route.append(nearest)
        visited.add(nearest)
        current = nearest

    return route


def cheapest_insertion_start(start_idx: int, dist: np.ndarray) -> List[int]:
    n = len(dist)
    route = [start_idx]
    remaining = set(range(n))
    remaining.remove(start_idx)

    if not remaining:
        return route

    second = min(remaining, key=lambda city: dist[start_idx, city])
    route.append(second)
    remaining.remove(second)

    while remaining:
        candidates = np.fromiter(sorted(remaining), dtype=int)
        route_array = np.asarray(route, dtype=int)
        next_array = np.roll(route_array, -1)
        deltas = (
            dist[np.ix_(candidates, route_array)]
            + dist[np.ix_(candidates, next_array)]
            - dist[route_array, next_array]
        )
        candidate_pos, edge_pos = np.unravel_index(np.argmin(deltas), deltas.shape)
        city = int(candidates[candidate_pos])
        route.insert(int(edge_pos) + 1, city)
        remaining.remove(city)

    return route


def two_opt(route: List[int], dist: np.ndarray) -> List[int]:
    best_route = route[:]
    n = len(best_route)

    while True:
        move = None
        for i in range(n - 1):
            for j in range(i + 2, n):
                if i == 0 and j == n - 1:
                    continue
                a = best_route[i]
                b = best_route[i + 1]
                c = best_route[j]
                d = best_route[(j + 1) % n]
                old_cost = dist[a, b] + dist[c, d]
                new_cost = dist[a, c] + dist[b, d]
                if new_cost < old_cost - 1e-9:
                    move = (i, j)
                    break
            if move is not None:
                break
        if move is None:
            return best_route
        i, j = move
        best_route[i + 1 : j + 1] = reversed(best_route[i + 1 : j + 1])



def solve_tsp(coords: np.ndarray, restarts: int = 8, seed: int = 0) -> Tuple[List[int], float]:
    """Solve the TSP using a multi-start greedy insertion and nearest-neighbor strategy with 2-opt."""
    dist = build_distance_matrix(coords)
    n = len(coords)
    best_route: List[int] | None = None
    best_cost = math.inf

    rng = np.random.default_rng(seed)
    start_indices = list(range(n)) if n <= restarts else list(rng.choice(n, size=restarts, replace=False))
    systematic_starts = [0, n // 2, n - 1]
    start_indices.extend(systematic_starts)
    start_indices = sorted(set(int(x) for x in start_indices if 0 <= x < n))

    for start in start_indices:
        for builder in (nearest_neighbor_start, cheapest_insertion_start):
            route = builder(start, dist)
            improved_route = two_opt(route, dist)
            cost = tour_length(improved_route, dist)
            if cost < best_cost:
                best_cost = cost
                best_route = improved_route

    if best_route is None:
        raise RuntimeError("No valid route could be generated")

    return best_route, float(best_cost)


def benchmark_all_instances(data_dir: str | Path) -> Dict[str, float]:
    results: Dict[str, float] = {}
    for path in sorted(Path(data_dir).glob("*.tsp")):
        coords = parse_tsp(path)
        _, cost = solve_tsp(coords, restarts=1, seed=1)
        results[path.stem] = cost
    return results

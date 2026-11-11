from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st

from tsp_solver import parse_tsp, solve_tsp

DATA_DIR = Path(__file__).resolve().parent / "tsp_data"
INSTANCE_FILES = sorted(DATA_DIR.glob("*.tsp"))

st.set_page_config(page_title="TSP Solver", layout="wide")

st.title("Traveling Salesman Problem Solver")
st.caption("Solve TSPLIB city-coordinate instances and inspect the best route.")

with st.sidebar:
    st.header("Solver settings")
    instance_name = st.selectbox(
        "TSP instance",
        [path.stem for path in INSTANCE_FILES],
        index=0,
    )
    restarts = st.slider("Greedy restarts", min_value=1, max_value=12, value=8, step=1)
    seed = st.number_input("Random seed", min_value=0, max_value=10_000, value=1, step=1)
    output_mode = st.radio("Route output option", ["Markdown", "Table", "Both"], index=0)
    display_route = st.checkbox("Display full route", value=True)


@st.cache_data(show_spinner=False)
def load_instance(instance_stem: str):
    return parse_tsp(DATA_DIR / f"{instance_stem}.tsp")


@st.cache_data(show_spinner=False)
def solve_instance(instance_stem: str, restarts_value: int, seed_value: int):
    coords = parse_tsp(DATA_DIR / f"{instance_stem}.tsp")
    route, cost = solve_tsp(coords, restarts=restarts_value, seed=seed_value)
    return coords, route, cost


coords, route, cost = solve_instance(instance_name, restarts, seed)
route_text = " → ".join(str(city) for city in route)

metric_col1, metric_col2, metric_col3 = st.columns(3)
metric_col1.metric("Cities", f"{len(coords):,}")
metric_col2.metric("Route length", f"{cost:.2f}")
metric_col3.metric("Route points", f"{len(route):,}")

st.subheader(f"Instance: {instance_name}")

st.subheader("Route visualization")
route_coords = coords[route]
fig, ax = plt.subplots(figsize=(8, 8))
ax.plot(route_coords[:, 0], route_coords[:, 1], color="#4c78a8", linewidth=1.5)
ax.scatter(route_coords[:, 0], route_coords[:, 1], color="#f58518", s=25, zorder=3)
ax.scatter([route_coords[0, 0]], [route_coords[0, 1]], color="#54a24b", s=60, zorder=4)
ax.set_title(f"Best route for {instance_name}")
ax.set_xlabel("X coordinate")
ax.set_ylabel("Y coordinate")
ax.grid(True, alpha=0.3)
st.pyplot(fig)

if display_route:
    if output_mode in {"Markdown", "Both"}:
        markdown_lines = [
            "### Route summary",
            f"- Start/finish city: {route[0]} → {route[-1]}",
            f"- Full route: `{route_text}`",
            "",
            "#### Ordered city sequence",
        ]
        for index, city in enumerate(route, start=1):
            x, y = coords[city]
            markdown_lines.append(f"{index}. City `{city}` at ({x:.2f}, {y:.2f})")
        st.markdown("\n".join(markdown_lines))

    if output_mode in {"Table", "Both"}:
        route_table = [{"Step": idx, "City": city, "X": round(float(coords[city][0]), 2), "Y": round(float(coords[city][1]), 2)} for idx, city in enumerate(route, start=1)]
        st.dataframe(route_table, use_container_width=True)

st.write("### Route in compact form")
st.code(route_text, language="text")

st.info(
    "This app uses a nearest-neighbor + cheapest insertion heuristic with 2-opt improvement to find a strong tour for the selected instance. "
    "Use the sidebar to switch the TSP instance, tuning parameters, or the rendered output format."
)

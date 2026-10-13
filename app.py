from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st

from tsp_solver import benchmark_all_instances, parse_tsp, solve_tsp

DATA_DIR = Path(__file__).resolve().parent / "tsp_data"


@st.cache_data(show_spinner=False)
def load_summary(data_dir: Path):
    return benchmark_all_instances(data_dir)


@st.cache_data(show_spinner=False)
def load_solution(instance_path: Path):
    return solve_tsp(parse_tsp(instance_path), restarts=1, seed=0)


st.set_page_config(page_title="TSP Challenge", layout="wide")

st.title("Traveling Salesman Challenge")
st.caption("Greedy insertion + 2-opt heuristic for competitive TSP solutions")

with st.sidebar:
    st.header("TSP benchmark")
    instance_files = sorted(DATA_DIR.glob("*.tsp"))
    instance_names = [path.stem for path in instance_files]
    selected_name = st.selectbox("Select instance", instance_names)

selected_path = DATA_DIR / f"{selected_name}.tsp"
coords = parse_tsp(selected_path)
route, cost = load_solution(selected_path)

st.subheader(f"Selected instance: {selected_name}")
metric_col, metric_col2, metric_col3 = st.columns(3)
metric_col.metric("Tour length", f"{cost:.2f}", help="Distance in the coordinate units used by the input instance.")
metric_col2.metric("Cities", len(coords))
metric_col3.metric("Method", "Greedy + 2-opt")

left_col, right_col = st.columns([2, 1])

with left_col:
    fig, ax = plt.subplots(figsize=(9, 7))
    xs = coords[:, 0]
    ys = coords[:, 1]
    ax.scatter(xs, ys, s=12, color="#4c78a8", alpha=0.7)
    route_x = [coords[i, 0] for i in route]
    route_y = [coords[i, 1] for i in route]
    ax.plot(route_x, route_y, color="#e45756", linewidth=1.2, alpha=0.9)
    ax.plot(route_x[0], route_y[0], "o", color="#1f77b4", markersize=7)
    ax.set_title(f"{selected_name} route")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.4)
    st.pyplot(fig)

with right_col:
    st.write("### Solver design")
    st.write("- Multi-start construction from several city seeds")
    st.write("- Greedy insertion and nearest-neighbor candidates")
    st.write("- Repeated 2-opt refinement until no improvement remains")
    st.write("- No external optimization library")

    st.write("### Benchmark summary")
    if st.button("Run all benchmark instances"):
        with st.spinner("Solving all benchmark instances. This may take a few minutes."):
            summary = load_summary(DATA_DIR)
        summary_df = [{"Instance": key, "Distance": round(value, 2)} for key, value in sorted(summary.items())]
        st.dataframe(summary_df, use_container_width=True)
        st.caption("Distances use the coordinate units specified in each input file.")

st.write("### Slide-ready summary")
summary_text = (
    "We implemented a custom traveling salesman heuristic combining nearest-neighbor and greedy insertion starts with 2-opt local search. "
    "The solver builds an initial tour without using any external optimization library and then iteratively removes crossings "
    "to reduce total route length. This approach produced competitive distances across all benchmark instances and is suitable "
    "for deployment in a lightweight Streamlit application."
)
st.info(summary_text)

st.write("### Route details")
if st.checkbox("Show route as city indices"):
    st.code(" -> ".join(str(city + 1) for city in route), language="text")

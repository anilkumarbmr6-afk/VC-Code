from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import streamlit as st

from bank_simulation import DAY_LENGTH_MINUTES, NUM_TELLERS, simulate_bank_day

st.set_page_config(page_title="Bank Branch Simulation", layout="wide")

st.title("Hands-on: Simulate a Bank Branch")
st.caption("Customer arrivals and teller service times are exponential; we model a shared queue with two tellers.")

with st.sidebar:
    st.header("Simulation controls")
    runs = st.slider("Monte Carlo runs", 50, 5000, 500, 50)
    seed = st.number_input("Random seed", min_value=1, max_value=999999, value=42, step=1)
    guess = st.number_input("Your guess for average wait (minutes)", min_value=0.0, value=0.0, step=0.5)

    st.markdown(
        """
        Problem setup
        - Customers arrive at random: one every 3 min on average
        - Service takes 4 min on average, also random
        - Both times are exponential
        - 2 tellers, one shared line, FIFO
        - Open one day: 8 hours (480 min)
        """
    )


@st.cache_data(show_spinner=False)
def load_results(runs_value: int, seed_value: int):
    return simulate_bank_day(runs=runs_value, seed=seed_value)


summary = load_results(runs, seed)

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
metric_col1.metric("Average wait", f"{summary.avg_wait:.2f} min")
metric_col2.metric("Worst wait", f"{summary.worst_wait:.2f} min")
metric_col3.metric("95th percentile", f"{summary.p95_wait:.2f} min")
metric_col4.metric("Teller busy %", f"{summary.teller_busy_pct:.1f}%")

if guess > 0:
    gap = abs(summary.avg_wait - guess)
    delta_text = f"Your guess is {gap:.2f} minutes away from the simulated average."
    if summary.avg_wait < guess:
        st.info(f"{delta_text} The simulation is a bit faster than your estimate.")
    else:
        st.info(f"{delta_text} The simulation is a bit slower than your estimate.")
else:
    st.info("Before you run it: guess the average wait with 2 tellers. Write the number down.")

st.subheader("Visual model: one shared line, two tellers")
fig, ax = plt.subplots(figsize=(11, 3.8))
ax.set_xlim(0, 11)
ax.set_ylim(0, 5)
ax.axis("off")


def draw_box(x, y, width, height, label, color):
    box = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.12",
        facecolor=color,
        edgecolor="#34495e",
        linewidth=1.5,
    )
    ax.add_patch(box)
    ax.text(x + width / 2, y + height / 2, label, ha="center", va="center", fontsize=11)


def draw_arrow(start, end):
    ax.add_patch(
        FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=15, color="#34495e", linewidth=1.5)
    )


draw_box(0.3, 1.9, 1.8, 1.2, "Arrivals\n(mean: 3 min)", "#d9eaf7")
draw_box(3.0, 1.6, 2.5, 1.8, "Shared FIFO queue\n(first come, first served)", "#fce8c3")
draw_box(6.6, 3.1, 1.8, 1.0, "Teller 1\n(mean service: 4 min)", "#d9f0e1")
draw_box(6.6, 0.9, 1.8, 1.0, "Teller 2\n(mean service: 4 min)", "#d9f0e1")
draw_box(9.2, 1.9, 1.5, 1.2, "Customer\nleaves", "#e7e1f4")

draw_arrow((2.1, 2.5), (3.0, 2.5))
draw_arrow((5.5, 2.7), (6.6, 3.5))
draw_arrow((5.5, 2.3), (6.6, 1.5))
draw_arrow((8.4, 3.5), (9.2, 2.8))
draw_arrow((8.4, 1.5), (9.2, 2.2))
ax.text(5.5, 4.65, "Exponential inter-arrival and service times", ha="center", fontsize=10, color="#555555")
st.pyplot(fig)
st.caption("The queue is shared: the next waiting customer goes to whichever teller becomes free first.")

left_col, right_col = st.columns([2, 1])

with left_col:
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(summary.wait_times, bins=25, color="#4c78a8", alpha=0.8, edgecolor="black")
    ax.axvline(summary.avg_wait, color="#e45756", linestyle="--", linewidth=2, label=f"Avg wait: {summary.avg_wait:.2f} min")
    ax.set_title("Customer wait-time distribution")
    ax.set_xlabel("Wait time (minutes)")
    ax.set_ylabel("Customers")
    ax.grid(True, alpha=0.3)
    ax.legend()
    st.pyplot(fig)

with right_col:
    st.write("### Queue facts")
    st.write(f"- Arrival rate: {60 / 3:.1f} people/hour")
    st.write(f"- Service rate: {60 / 4:.1f} people/hour per teller")
    st.write(f"- Tellers: {NUM_TELLERS}")
    st.write(f"- Day open: {DAY_LENGTH_MINUTES:.0f} minutes")
    st.write(f"- Customers served: {summary.total_customers:,}")

st.write("### Simulated output")
summary_df = [
    {"Metric": "Average wait (min)", "Value": round(summary.avg_wait, 2)},
    {"Metric": "Worst wait (min)", "Value": round(summary.worst_wait, 2)},
    {"Metric": "95th percentile wait (min)", "Value": round(summary.p95_wait, 2)},
    {"Metric": "Teller busy %", "Value": round(summary.teller_busy_pct, 2)},
    {"Metric": "Customers served", "Value": summary.total_customers},
]
st.dataframe(summary_df, use_container_width=True)

st.write("### Slide-ready summary")
st.info(
    "With two tellers, the shared-queue model gives a typical customer wait in the low single-digit minutes range, "
    "while the busiest cases can still stretch much longer. The simulation also shows teller utilization stays well below 100% "
    "because arrivals and service times are both random, but the system is still busy enough to create queues during peaks."
)

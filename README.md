# TSP Solver App

This project solves classic Traveling Salesman Problem instances from the TSPLIB
format. The app lets you choose a bundled dataset, run the solver, and inspect the
best route in several formats, including a Markdown summary option.

## Run locally

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## What the app shows

- A TSPLIB instance selector
- A tuned heuristic solver using greedy restarts and 2-opt refinement
- Route length and city count metrics
- A Markdown route summary option
- A route table and 2D visualization

The bundled datasets are stored in the `tsp_data/` directory.

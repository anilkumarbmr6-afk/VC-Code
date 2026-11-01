# Bank Branch Simulation

This project simulates a bank branch with a single shared queue and two tellers.
Customers arrive on an exponential schedule with an average inter-arrival time of
3 minutes, and each teller serves customers with an exponential service time
average of 4 minutes. The app runs a Monte Carlo-style simulation and reports
average wait, worst wait, 95th percentile wait, and teller utilization.

## Run locally

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io) with GitHub.
2. Choose **Create app**, select this repository and the
   `deploy/bank-branch-simulation` branch, and set the main file path to
   `app.py`.
3. Deploy. Streamlit installs the dependencies from `requirements.txt`.

## What the app shows

- Your pre-run guess for average wait time
- A Monte Carlo simulation of the queueing system
- A wait-time histogram for the simulated customers
- Summary metrics for the branch performance

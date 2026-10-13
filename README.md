# Traveling Salesman Challenge

A Streamlit app for visualizing custom TSP solutions on the included benchmark
instances. The solver uses multi-start nearest-neighbor and greedy insertion,
followed by 2-opt local search; it does not use an external optimization
library.

## Run locally

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this project to a GitHub repository. The `.gitignore` excludes the
   session slide PDFs, notebook, and local environment.
2. In [Streamlit Community Cloud](https://share.streamlit.io), choose **Create
   app**, select the repository and branch, and set the main file path to
   `app.py`.
3. Deploy. The benchmark datasets in `tsp_data/` must remain in the repository.

# AI Government Scheme Finder

Streamlit app for checking eligibility, generating scheme recommendations, chatting about the scheme catalog, and exporting a summary report.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project structure

- `app.py` is the main entrypoint.
- `pages/` contains Streamlit page wrappers.
- `utils/` contains shared loaders, eligibility logic, ranking, UI rendering, and PDF export.
- `data/schemes.csv` holds the default scheme catalog.

## Deployment

The app is ready for Streamlit Community Cloud or any environment that supports Streamlit.

Use `app.py` as the entrypoint and ensure `requirements.txt` is installed.

If you want to replace the starter data, update `data/schemes.csv` with the same column names:

- `scheme_name`
- `category`
- `description`
- `age_min`
- `age_max`
- `income_max`
- `occupations`
- `states`
- `eligible_categories`
- `benefits`
- `link`
- `keywords`

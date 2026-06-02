# NEXUS BackEnd

Independent FastAPI backend for NEXUS, an AI-powered Pacific agriculture data visualization platform.

## What It Does

- Loads CSV and Excel files from `app/data/raw`
- Normalizes country, product, type, year, yield, and unit columns
- Handles missing country/product/year/value rows safely
- Serves REST endpoints for charts, filters, comparisons, country profiles, and Nexus AI placeholder responses
- Keeps Supabase and Gemini integration modular for later phases

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

## Data

Place official Pacific Dataviz Challenge CSV or Excel files in:

```text
app/data/raw
```

The loader accepts `.csv`, `.xlsx`, and `.xls`.

Expected or auto-detected columns:

- `country`
- `product`
- `type` (`crop` or `livestock`)
- `year`
- `yield`
- `unit`

Common alternatives such as `area`, `item`, `commodity`, `value`, and `units` are also normalized. The included `nexus_sample_yields.csv` is only a starter file so the API can be tested before official data is added.

## Endpoints

- `GET /api/health`
- `GET /api/summary`
- `GET /api/countries`
- `GET /api/products?type=crop`
- `GET /api/products?type=livestock`
- `GET /api/filters`
- `GET /api/trends?country=Fiji&product=Taro&type=crop`
- `GET /api/comparison?product=Taro&type=crop&year=2021`
- `GET /api/country-profile?country=Fiji`
- `POST /api/ask`

Example `POST /api/ask` body:

```json
{
  "question": "How has Fiji taro changed over time?"
}
```

## Frontend Integration

CORS is enabled for:

- `http://localhost:3000`
- `http://localhost:5173`
- `https://your-nexus-frontend.vercel.app`

Update `.env` when the final Vercel frontend URL is known.

## Future Work

- Replace or supplement file loading with Supabase PostgreSQL
- Add Gemini 2.5 Flash in `app/services/gemini_service.py`
- Build richer dataset context for natural language questions
- Add tests after the official dataset schema is finalized


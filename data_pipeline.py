import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import anthropic
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

load_dotenv(Path(__file__).parent / ".env")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

DATA_DIR = Path(__file__).parent / "data"
REPORTS_DIR = Path(__file__).parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


# Reads the CSV file into a Pandas DataFrame, removes missing values and duplicates, converts date strings to date objects, and ensures revenue is numeric — making messy real-world data usable
def load_and_clean(filepath: str) -> pd.DataFrame:
    print(f"  Loading data from: {filepath}")
    df = pd.read_csv(filepath)
    print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")
    df = df.dropna()
    df["date"] = pd.to_datetime(df["date"])
    df = df.drop_duplicates()
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0)

    print(f"  After cleaning: {len(df)} rows")
    return df


# Takes the cleaned DataFrame and computes all key business metrics — total revenue, average deal size, breakdowns by region, category, sales rep, and month, plus top performers in each group
def compute_metrics(df: pd.DataFrame) -> dict:
    total_revenue = float(df["revenue"].sum())
    total_sales = int(len(df))
    avg_deal_size = float(df["revenue"].mean())

    by_region = df.groupby("region").agg(
        revenue=("revenue", "sum"),
        transactions=("revenue", "count")
    ).to_dict()

    by_category = df.groupby("category").agg(
        revenue=("revenue", "sum"),
        transactions=("revenue", "count")
    ).to_dict()

    by_rep = df.groupby("sales_rep").agg(
        revenue=("revenue", "sum"),
        transactions=("revenue", "count")
    ).to_dict()

    by_month = df.groupby(df["date"].dt.to_period("M"))["revenue"].sum()
    monthly = {str(k): float(v) for k, v in by_month.items()}

    top_product = df.groupby("product")["revenue"].sum().idxmax()
    top_region = df.groupby("region")["revenue"].sum().idxmax()
    top_rep = df.groupby("sales_rep")["revenue"].sum().idxmax()

    return {
        "total_revenue":   total_revenue,
        "total_sales":     total_sales,
        "avg_deal_size":   avg_deal_size,
        "by_region":       by_region,
        "by_category":     by_category,
        "by_rep":          by_rep,
        "monthly_revenue": monthly,
        "top_product":     top_product,
        "top_region":      top_region,
        "top_rep":         top_rep,
    }


# Sends the computed metrics to Claude as structured JSON and receives a written business insight report with executive summary, breakdowns, key findings, and recommended actions
def generate_analysis(metrics: dict) -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""You are a business analyst reviewing sales pipeline data
for an AI automation agency. Write a structured insight report based on
the metrics below. Include:

1. Executive Summary (3 sentences — overall performance)
2. Revenue Analysis (total, trends, monthly breakdown)
3. Regional Performance (which regions are strongest and why)
4. Category Breakdown (which service categories drive most revenue)
5. Sales Rep Performance (top performer and recommendations)
6. Key Insights (3 bullet points — most important findings)
7. Recommended Actions (3 specific next steps)

Be specific. Use the actual numbers. Write for a business owner.

Sales Data Metrics:
{json.dumps(metrics, indent=2)}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


# Orchestrates the full pipeline — load and clean the CSV, compute metrics, generate AI analysis, save the full report as a timestamped .txt file, and return all results
def run_pipeline(data_file: str = "sales_data.csv") -> dict:
    filepath = DATA_DIR / data_file
    print(f"\nRunning pipeline on: {filepath}")

    df = load_and_clean(str(filepath))
    metrics = compute_metrics(df)
    print("  Metrics computed")

    analysis = generate_analysis(metrics)
    print("  AI analysis complete")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORTS_DIR / f"analysis_{timestamp}.txt"
    report_path.write_text(
        f"DATA PIPELINE ANALYSIS\n"
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Source: {data_file}\n"
        f"{'='*60}\n\n"
        f"METRICS SUMMARY\n{'='*60}\n"
        f"{json.dumps(metrics, indent=2)}\n\n"
        f"AI ANALYSIS\n{'='*60}\n"
        f"{analysis}",
        encoding="utf-8"
    )
    print(f"  Report saved: {report_path}")

    return {"metrics": metrics, "analysis": analysis, "saved_to": str(report_path)}


app = FastAPI()


class PipelineRequest(BaseModel):
    data_file: str = "sales_data.csv"


@app.get("/")
def health():
    return {"status": "running", "system": "Data Pipeline with AI Analysis"}


@app.post("/analyse")
async def analyse(request: PipelineRequest):
    result = run_pipeline(request.data_file)
    return {
        "analysis": result["analysis"],
        "saved_to": result["saved_to"],
        "total_revenue": result["metrics"]["total_revenue"],
        "total_sales":   result["metrics"]["total_sales"],
        "top_product":   result["metrics"]["top_product"],
        "top_region":    result["metrics"]["top_region"],
        "top_rep":       result["metrics"]["top_rep"],
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)

# Automated Data Pipeline with AI Analysis

## What this does
A Python pipeline that reads a CSV sales dataset, cleans and transforms
it using Pandas, computes key business metrics automatically, sends the
summary statistics to Claude for AI analysis, and produces a structured
insight report saved as a timestamped file. Runs with one command and
is exposed as a FastAPI HTTP endpoint triggerable from any tool.

## The problem it solves
Most business data sits unread in spreadsheets. Someone manually exports
a CSV, spends hours cleaning it, makes charts, writes observations, and
sends a report. Next month the same process repeats from scratch. This
pipeline does the entire thing in under 30 seconds; cleaning, analysis,
and a written insight report automatically, every time.

## Measurable result
- Rows processed: 15 sales records across 5 months
- Cleaning steps automated: missing values, duplicates, date formatting,
  numeric conversion
- Metrics computed: total revenue, average deal size, revenue by region,
  category, sales rep, and month
- AI insight report generated: yes; with executive summary, breakdowns,
  key insights, and recommended actions
- Report saved as timestamped .txt file: yes

## Tech stack: 2026 versions
- Python 3.12.0
- Pandas 2.x
- Anthropic SDK 0.40+
- Claude claude-sonnet-4-6
- FastAPI + Uvicorn
- python-dotenv

## Tools used and why

### Pandas: the data processor
Reads the CSV file into a DataFrame and handles all cleaning and
transformation. Removes missing values, converts date strings to date
objects, drops duplicates, and groups data by region, category, and
sales rep. Turns 15 rows of raw data into a clean business dashboard
in under 10 lines of code.

### Claude API: the analyst
Receives the cleaned summary metrics and writes a structured business
insight report. Identifies trends, flags top performers, and recommends
specific next actions. Turns numbers into narrative a business owner
can read and act on immediately.

### FastAPI: the API layer
Exposes the pipeline as a POST /analyse endpoint. Accepts an optional
data_file parameter so different CSV files can be analysed without
changing the code. Triggerable from n8n, Make.com, or any HTTP client.

### pathlib + datetime: report management
Saves every report as a uniquely timestamped .txt file so no analysis
is ever overwritten and a full history of reports is maintained.

### python-dotenv: key management
Loads the Anthropic API key from .env so it is never hardcoded in
the script or exposed on GitHub.

## How it works
1. POST request arrives at /analyse with optional data_file parameter
2. Pandas reads the CSV and cleans the data
3. Pipeline computes total revenue, deal size, regional breakdown,
   category breakdown, sales rep performance, and monthly trends
4. Summary metrics sent to Claude with a business analyst prompt
5. Claude writes a structured insight report with 7 sections
6. Full report saved as a timestamped .txt file in reports/
7. Response returned with analysis, key metrics, and file path

## Metrics computed automatically
- Total revenue and total number of sales
- Average deal size
- Revenue and transaction count by region
- Revenue and transaction count by category
- Revenue and transaction count by sales rep
- Monthly revenue trend
- Top product, top region, and top sales rep

## Adding your own data
Replace sales_data.csv with your own CSV file. Make sure the header
row matches exactly: date, product, category, region, quantity,
unit_price, revenue, sales_rep. Drop the file in the data/ folder
and pass the filename in the request body.

## Error handling
- ModuleNotFoundError pandas: run pip install pandas
- FileNotFoundError: confirm sales_data.csv is in the data/ folder
- Port 8002 in use: run netstat -ano | findstr :8002 then
  taskkill /PID [id] /F
- KeyError on groupby: check CSV header row matches expected column names
  exactly with no spaces or capital letters
- Revenue conversion error: remove currency symbols and commas from
  revenue values in the CSV

## Screenshots
[https://imgur.com/fPtc9NN]
[https://imgur.com/WjWin9k]
[https://imgur.com/undefined]
[https://imgur.com/BuGqFnz]


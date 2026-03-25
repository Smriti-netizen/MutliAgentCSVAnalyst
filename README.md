# Multi-Agent CSV Analyst

A multi-agent data analysis tool built with **LangGraph**, **Google Gemini**, and **Streamlit**. Upload any CSV file, ask questions in plain English, and receive a verified Markdown report -- powered by four autonomous AI agents that write code, execute it safely, generate insights, and fact-check the results.

## Architecture

```
User uploads CSV + asks a question
        |
        v
  [Profiler] --> extracts schema, dtypes, sample rows (only this goes to the LLM)
        |
        v
  [Coder Agent] --> generates Pandas code using Gemini
        |
        v
  [Executor Agent] --> runs code in a sandboxed environment
        |
        |-- ERROR? --> back to Coder with traceback (up to 3 retries)
        |
        v  SUCCESS
  [Analyst Agent] --> writes a Markdown report from code output
        |
        v
  [Reviewer Agent] --> fact-checks every number in the report
        |
        |-- REJECTED? --> back to Analyst with feedback (up to 3 retries)
        |
        v  APPROVED
  Final Report (displayed + downloadable as .docx)
```

## Key Design Decisions

- **Privacy**: Full CSV data never leaves your machine. Only column names, dtypes, and 5 sample rows are sent to the LLM.
- **Safety**: Generated code runs in a restricted `exec()` sandbox. Only `pandas`, `numpy`, and the loaded DataFrame are accessible. File I/O, imports, and OS commands are blocked.
- **Accuracy**: A dedicated Reviewer agent compares every number in the report against the raw code output, rejecting hallucinated or misinterpreted results.
- **Retry loops**: Both code generation and report writing have automatic retry mechanisms (max 3), making the pipeline self-healing.

## Quick Start

### 1. Clone the repo

```bash
git clone git@github.com:Smriti-netizen/MutliAgentCSVAnalyst.git
cd MutliAgentCSVAnalyst
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up your API key

Get a free Gemini API key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

```bash
cp .env.example .env
# Edit .env and paste your key
```

### 4. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

### 5. Try it

- Click **"Load sample dataset"** to use the bundled telecom churn data, or upload your own CSV(s).
- Ask a question like: *"What is the churn rate by contract type?"*
- Click **Analyze** and watch the agents work.
- Download the report as a `.docx` file.

## Project Structure

```
├── app.py                      # Streamlit UI entry point
├── requirements.txt            # Python dependencies
├── .env.example                # API key template
├── .gitignore                  # Git ignore rules
├── assets/
│   └── icon.png                # App favicon
├── agents/
│   ├── state.py                # LangGraph shared state (TypedDict)
│   ├── graph.py                # LangGraph graph: nodes + conditional edges
│   ├── coder.py                # Agent 1: generates Pandas code via Gemini
│   ├── executor.py             # Agent 2: runs code in sandbox
│   ├── analyst.py              # Agent 3: writes Markdown report
│   └── reviewer.py             # Agent 4: LLM-as-judge fact-checker
├── utils/
│   ├── data_profiler.py        # CSV schema extraction (sent to LLM)
│   └── sandbox.py              # Restricted exec() environment
└── sample_data/
    └── churn.csv               # Demo dataset (100-row telecom churn)
```

## Upload Limits

| Limit          | Value  |
|----------------|--------|
| Max files      | 5      |
| Max per file   | 10 MB  |
| Max total      | 25 MB  |

## Tech Stack

| Component          | Technology                          |
|--------------------|-------------------------------------|
| LLM                | Google Gemini 2.5 Flash (free tier) |
| Agent orchestration| LangGraph                           |
| LLM integration    | langchain-google-genai              |
| Web UI             | Streamlit                           |
| Data processing    | pandas, numpy                       |
| Report export      | python-docx                         |


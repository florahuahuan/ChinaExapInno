# AI-assisted screening of annual reports and financial news

**Research companion:** *A patent citation dataset for studying potential exaptive technological redeployment in China*

## Overview

This repository documents the Python workflow used to collect, prepare, and screen corporate annual reports and financial news for textual accounts of technological redeployment and serendipitous innovation among Chinese listed firms. The screening uses a structured Chinese-language prompt and DeepSeek-R1 through the SiliconFlow API.

The workflow covers document collection and preparation, AI-assisted extraction, structured output processing, and review of relevant textual passages. The annual-report processing scripts are provided below. Financial news is a second textual source used in the research; its collection-specific scripts are not included in the current repository structure.

## Repository structure

```text
README.md
requirements.txt
.gitignore
company_details.csv
scripts/
  00_crawl_annual_reports.py
  01_clean_annual_reports.py
  02_download_annual_report_pdfs.py
  03_extract_pdf_text.py
  prompt.py
  04_run_deepseek_extraction.py
  format_to_json.py
  summarize_jsonl.py
data/
  szse_stock.json
```

### Main files

| File | Purpose |
| --- | --- |
| `company_details.csv` | Company and stock information used to identify firms for document collection |
| `data/szse_stock.json` | Stock identifier lookup used by the annual-report crawler |
| `scripts/00_crawl_annual_reports.py` | Retrieve annual-report announcement metadata from CNINFO |
| `scripts/01_clean_annual_reports.py` | Clean announcement records and prepare firm/report lists |
| `scripts/02_download_annual_report_pdfs.py` | Download annual-report PDFs |
| `scripts/03_extract_pdf_text.py` | Extract text from PDF documents |
| `scripts/prompt.py` | Chinese-language screening instructions and structured output fields |
| `scripts/04_run_deepseek_extraction.py` | Submit document text to DeepSeek-R1 and save results |
| `scripts/format_to_json.py` | Parse and format structured model responses |
| `scripts/summarize_jsonl.py` | Summarize saved JSONL screening results |
| `requirements.txt` | Python package dependencies |

## Software environment

- **Python:** 3.13.3
- **LLM:** `deepseek-ai/DeepSeek-R1`
- **API provider:** SiliconFlow (`https://api.siliconflow.cn/v1`)
- **Text extraction:** `pdfplumber`
- **Token estimation:** `tiktoken`, encoding `o200k_base`
- **Structured output:** JSON Lines (`.jsonl`)

Install the Python dependencies from the repository root:

```bash
python -m venv .venv
# Activate the virtual environment for your operating system.
python -m pip install -r requirements.txt
```

## Text sources and processing workflow

### 1. Corporate annual reports

Annual-report announcements are retrieved from **CNINFO**. The workflow uses `company_details.csv` for company information and `data/szse_stock.json` for stock identifier lookup.

| Step | Script | Main input | Main output |
| --- | --- | --- | --- |
| Retrieve announcements | `00_crawl_annual_reports.py` | `company_details.csv`, `szse_stock.json` | `年报.csv` |
| Clean and organize records | `01_clean_annual_reports.py` | `年报.csv`, `company_details.csv` | `年报清洗.xlsx`, `统计结果.xlsx`, `随机选取30个股票.xlsx`, `最终整理年报.xlsx` |
| Download reports | `02_download_annual_report_pdfs.py` | `最终整理年报.xlsx` | PDF files in `pdfs/` |
| Extract text | `03_extract_pdf_text.py` | Downloaded PDFs | TXT files in `txts/` |
| Run AI screening | `04_run_deepseek_extraction.py` | TXT files and `prompt.py` | `label_jsons/deepseek_results.jsonl` |

The annual-report metadata crawler is configured for **2001–2024**. The cleaning script organizes company-year announcements and uses `numpy.random.seed(1)` in its sampling routine. PDF files are converted to machine-readable text using `pdfplumber`.

**Input configuration:** The filenames in this README describe the intended repository inputs. If the local Python scripts still reference the former Excel filename (`行业股票.xlsx`), update their file paths and CSV-loading commands to read `company_details.csv` before execution.

### 2. Financial news

Financial news provides additional descriptions of companies' technological developments, unexpected applications, opportunity recognition, and commercialization activities. Relevant articles can be collected and converted into text documents for screening with the same Chinese-language prompt and DeepSeek-R1 extraction procedure.

For each article, retain the company identifier, title, publisher, publication date, source URL, and extracted text where available. News collection and preprocessing scripts can be added to `scripts/` when prepared for release.

### 3. AI-assisted textual screening

The screening script reads prepared TXT files, sends their contents to DeepSeek-R1, and saves the model's structured responses as JSONL records. The same extraction framework can be applied to prepared annual-report and financial-news text files.

Key settings in the supplied runner are:

| Setting | Configuration |
| --- | --- |
| Model identifier | `deepseek-ai/DeepSeek-R1` |
| System prompt | `PROMPT` in `scripts/prompt.py` |
| Input | Text from a selected document |
| `MAX_DOC_TOKENS` | 80,000 |
| `PROMPT_HEADROOM` | 1,024 |
| `MIN_WINDOW_TOKENS` | 1,500 |
| Long-document handling | Selects a central contiguous text window when needed |
| Concurrent workers | 5 |
| Output file | `label_jsons/deepseek_results.jsonl` |
| Output format | One JSON object per line |

### Example execution

Set the API credentials and input/output paths before running the extraction script. On macOS or Linux:

```bash
export OPENAI_API_KEY="YOUR_API_KEY"
export MD_GLOB="/path/to/txts/**/*.txt"
export SAVE_DIR="label_jsons"
export RESULT_FILE="label_jsons/deepseek_results.jsonl"
python scripts/04_run_deepseek_extraction.py
```

On Windows, set the same environment variables using PowerShell or Command Prompt syntax. The paths in the scripts may need to be adapted to the local folder structure.

## Screening framework

The Chinese-language prompt in `scripts/prompt.py` organizes screening around six dimensions:

| Dimension | Screening focus |
| --- | --- |
| Overall signal | Textual indications of serendipitous innovation or technological redeployment |
| Non-anticipation | Whether an application differs from the initially stated objectives |
| Opportunity recognition | Recognition of an additional technological or market opportunity |
| Commercial value | Reported products, deployments, customers, contracts, or commercial outcomes |
| Technological or functional transfer | Reuse of technological knowledge, components, methods, or functions in another application |
| Accidental discovery | Descriptions of unexpected discoveries or uses |

The prompt also requests supporting explanations and contextual fields, including keywords, illustrative cases, technologies involved, R&D background, strategic alignment, market transformation, and possible causes.

## Structured output

The runner writes one record per processed document to a JSONL file. A simplified record is shown below:

```json
{
  "doc_id": "example.txt",
  "md_path": "/path/to/example.txt",
  "response": {
    "serendipity_innovation": {
      "迹象": {
        "结果": "有",
        "说明": "..."
      }
    }
  }
}
```

The complete Chinese-language output structure is defined in `scripts/prompt.py`. Main branches include:

| Field | Content |
| --- | --- |
| `serendipity_innovation.迹象` | Overall signal and explanation |
| `serendipity_innovation.识别维度.非预期性` | Non-anticipation |
| `serendipity_innovation.识别维度.机会识别` | Opportunity recognition |
| `serendipity_innovation.识别维度.商业价值转化` | Commercial value |
| `serendipity_innovation.技术或功能转移` | Technological or functional transfer |
| `serendipity_innovation.是否偶然发现` | Accidental discovery |
| `serendipity_innovation.关键词` | Relevant keywords |
| `serendipity_innovation.案例` | Described cases |

`scripts/format_to_json.py` parses and formats model responses. `scripts/summarize_jsonl.py` provides summary counts from saved screening records. Relevant passages can then be reviewed against the source annual reports and news articles.

## Document review and source records

For annual reports, useful source metadata include company name, stock code, reporting year, announcement date, and original document URL. For financial news, useful fields include company name, article title, publisher, publication date, and original URL.

Review of retrieved passages focuses on the description of the original technology, the subsequent application, the circumstances of opportunity recognition, and any reported commercial outcomes. These source records support the interpretation and presentation of textual examples.

## Data access and responsible use

The repository shares scripts, prompts, and workflow documentation. Users should obtain source annual reports and news articles from their respective providers and observe applicable copyright and access conditions. API credentials should be stored privately and excluded from GitHub commits.


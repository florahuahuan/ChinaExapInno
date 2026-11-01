[README.md](https://github.com/user-attachments/files/34232640/README.md)
# LLM-assisted qualitative corroboration of potential exaptation in Chinese listed companies

## Scope and interpretation

This repository documents the **available** implementation of annual-report collection, preparation, DeepSeek-R1 structured extraction, and manual qualitative interpretation. It supports a **qualitative textual-corroboration** component. 

## Repository contents

```text
README.md                                Method, status, execution order, environment and output definitions
requirements.txt                         Packages imported by supplied scripts (historical versions unknown)
.gitignore                               Excludes keys, downloaded documents and large raw outputs
scripts/
  00_crawl_annual_reports.py                               Retrieve CNINFO annual-report announcement metadata
  01_clean_annual_reports.py                         Select company-year announcements and sampled firm lists
  02_download_annual_report_pdfs.py                            Download annual-report PDF files
  03_extract_pdf_text.py                       Extract text from readable PDFs
  prompt.py                               Original Chinese-language coding instructions and expected JSON-like layout
  04_run_deepseek_extraction.py           DeepSeek-R1 request and JSONL result-writing script
  format_to_json.py                       Parse, extract and attempt to repair JSON responses
  summarize_jsonl.py                      OPTIONAL retrospective count of saved structured outputs
  
data/
  szse_stock.json                         Author-supplied stock-ID lookup (check redistribution rights)
templates/
  manual_review_template.csv              Empty evidence and screening-log template; not historical review results
docs/
  Part_III_revised.md                     Proposed revised manuscript wording
  Reviewer_response_draft.md              Draft response with explicitly stated limitations
```

The scripts in `scripts/` are publication-oriented copies of the supplied files. **Security-only adjustments** were made to the API runner and announcement crawler (TLS certificate verification enabled; API URL switched to HTTPS; API-key fragments and full server response are no longer printed in logs). They retain the original study's prompt, model identifier, conceptual extraction, token window, thread count and output record structure. Thus, these are not byte-for-byte archival copies of the historical local scripts; preserve originals in a private research archive if exact provenance is required.

## Processing stages and script order

| Stage | Script | Inputs | Outputs | Implementation notes |
| --- | --- | --- | --- | --- |
| 1. Annual-report metadata | `scripts/00_crawl_annual_reports.py` | `行业股票.xlsx`, `data/szse_stock.json` (place beside script or adjust path), CNINFO endpoint | `年报.csv` | Loops over requested years **2001–2024**. Uses page size 30 but does not explicitly paginate additional results; check completeness. |
| 2. Clean and sample | `scripts/01_clean_annual_reports.py` | `年报.csv`, `行业股票.xlsx` | `年报清洗.xlsx`, `统计结果.xlsx`, `随机选取30个股票.xlsx`, `最终整理年报.xlsx` | Keeps latest **announcement** per firm/calendar year; firms with at least 10 such records eligible; samples 30 firms per board with `numpy.random.seed(1)`. This is not proof that all initially collected reports were LLM-processed. |
| 3. PDF download | `scripts/02_download_annual_report_pdfs.py` | `最终整理年报.xlsx` | `pdfs/<board>/<code>_<firm>_<reportyear>.pdf` | Uses 10 workers and extracts the report year from title. |
| 4. PDF-to-TXT | `scripts/03_extract_pdf_text.py` | `pdfs/*/*.pdf` | `txts/<board>/<file>.txt` | Uses `pdfplumber`, 10 workers. Text must be extractable; scanned/image-only pages are not OCR-processed. |
| 5. Structured LLM extraction | `scripts/04_run_deepseek_extraction.py` with `scripts/prompt.py` and `scripts/format_to_json.py` | A glob of TXT files and API credentials via environment variable | `label_jsons/deepseek_results.jsonl` | Defaults and exact JSONL fields below. Resumes by `doc_id`; failures may not appear in the output. |
| 6. Manual case review | **Human procedure, not a supplied automated script** | Original documents, model outputs, patent texts/claims | Completed review log / case narratives | See four criteria and template below. Historical complete case-count ledger was not provided. |

**Important input limitations:** `行业股票.xlsx` was NOT part of the provided files and is required for Stages 1–3. The annual-report scripts do not establish the exact text-record totals stated in the manuscript; a complete execution manifest must be reconstructed from actual input/output files. The separate Sohu-news crawler, merger, LLM annotator and export scripts described in the authors' earlier documentation were **not supplied in this package**. Consequently, the **news** workflow is documented at a high level but cannot be reproduced end-to-end from the available scripts.

## Software environment and installation

The original Python version and dependency versions were not provided. `requirements.txt` lists the **package names** imported by the supplied code; it is not a historically pinned environment. To reproduce exact behavior, the authors must add a verified Python version, tested package versions, and ideally an environment lockfile.

Suggested setup for a new test environment (not proof of the historical environment):

```bash
python -m venv .venv
# Activate .venv for your operating system, then:
python -m pip install -r requirements.txt
```

The scripts were designed around local folders and input files. Set working directories and input paths as appropriate; changing path configuration does not change the coding framework.

## Model and prompt configuration: settings visible in the supplied code

| Item | Value / qualification |
| --- | --- |
| API provider | SiliconFlow (`https://api.siliconflow.cn/v1` in the publication-safe copy) |
| Default model ID | `deepseek-ai/DeepSeek-R1` (overridable through `OPENAI_MODEL`) |
| Model access date | **Not recovered; authors must supply a verified date or date range** |
| Immutable model build or version snapshot | **Not available in supplied scripts** |
| Historical temperature and top-p | Not explicitly set in the request payload; effective provider defaults not recorded |
| Actual system message | Full `PROMPT` string from `scripts/prompt.py` |
| Actual user message | Text extracted from one selected annual-report TXT file |
| Token counting | `tiktoken` encoding `o200k_base` (a budgeting approximation, not necessarily the provider's exact tokenizer) |
| `MAX_DOC_TOKENS` | 80,000 by default |
| `PROMPT_HEADROOM` | 1,024 by default |
| `MIN_WINDOW_TOKENS` | 1,500 by default |
| Long-text operation | Keeps a **central contiguous** text segment, not the full beginning and end and not chunk-by-chunk coverage |
| Parallelism | Five request workers (`ThreadPoolExecutor(max_workers=5)`) |
| Generation payload | Model, system/user messages, `stream: false`; no explicit JSON schema or `response_format` enforcement |
| JSON handling | `format_to_json.py` attempts direct parsing, wrapper removal, first-object extraction and `json_repair`; **does not independently verify schema semantics** |
| Output | Append-only JSON Lines at `label_jsons/deepseek_results.jsonl` by default |

To run the LLM processing stage from the repository root, an example is:

```bash
export OPENAI_API_KEY="<YOUR_PRIVATE_KEY>"   # set privately; do not commit
export MD_GLOB="/path/to/your/txts/**/*.txt"
export SAVE_DIR="label_jsons"
export RESULT_FILE="label_jsons/deepseek_results.jsonl"
# prompt.py and format_to_json.py reside beside the runner:
python scripts/04_run_deepseek_extraction.py
```

When running on Windows, use the appropriate command-shell syntax for environment variables. The runner's historical default `MD_GLOB` was a local Windows path and **will not work unchanged on another computer**. A `doc_id` is currently derived from the file basename, which may collide if folders contain identically named files; verify uniqueness and, if needed, change the public execution setup **with the change documented**. The existing output also skips records with previously seen `doc_id` values; a new clean test run should use a new result file.

### Record-level output schema

Each JSONL line has the outer structure:

```json
{"doc_id":"example.txt","md_path":"/path/example.txt","response":{"serendipity_innovation":{"迹象":{"结果":"有","说明":"..."}}}}
```

The original `prompt.py` is authoritative for the complete **Chinese-language** nested output shape. Core branches include:

| Output branch | Interpretation |
| --- | --- |
| `serendipity_innovation.迹象` | Overall textual serendipity-related signal and explanation |
| `serendipity_innovation.识别维度.非预期性` | Non-anticipation and explanation |
| `serendipity_innovation.识别维度.机会识别` | Opportunity recognition and explanation |
| `serendipity_innovation.识别维度.商业价值转化` | Commercial value and explanation |
| `serendipity_innovation.技术或功能转移` | Technological or functional transfer and explanation |
| `serendipity_innovation.是否偶然发现` | Accidental discovery and explanation |
| `serendipity_innovation.关键词` | Keywords as cues, not proof |
| `serendipity_innovation.案例`, `涉及技术`, `技术类型`, `研发投入背景`, `战略一致性`, `市场转化`, `可能原因` | Context and explanatory fields |

A *validly parsed* JSON object is **not** necessarily a valid evidence-backed judgment. The prompt includes predefined example-shaped case fields and keywords. Source quotations, pages and evidence locations must be checked manually rather than assumed to have been extracted reliably.

## Coding framework: six analytical dimensions

| Dimension | Operational question | Needed corroborating information |
| --- | --- | --- |
| Overall signal | Does the text contain a candidate narrative associated with technological redeployment or serendipity? | Source-supported description, not just a model-generated label |
| Non-anticipation | Is the later application absent from, or inconsistent with, the original goal? | Initial objectives contrasted with later outcomes |
| Opportunity recognition | Was an additional use or opportunity identified? | Documentary account of recognition, not merely market presence |
| Commercial value | Was an actual economic or commercial result reported? | Products, deployments, customers or contracts; distinguish plans from outcomes |
| Technological/functional transfer | Is an underlying technology retained and put to a different use? | Technical-content continuity and changed application/function |
| Accidental discovery | Was the use discovered unexpectedly? | Direct narrative evidence; not inferred from IPC differences |

Keywords are **retrieval cues**, not necessary or sufficient criteria for exaptation. Planned expansion is not automatically non-anticipated, and a cross-IPC relationship alone does not establish a retained technical mechanism.

## Manual review and case selection

Four author-provided review criteria were applied conceptually:

1. Identify the original technology and its initial application.
2. Establish evidence of a later change of function or application.
3. Examine continuity in underlying technical content.
4. Assess available evidence regarding whether the later application was non-anticipated.

Researchers should preserve supporting document identifier, URL/filename, date, page or paragraph, patent number, claim/description location, and a decision with an explanatory limitation in `templates/manual_review_template.csv`. The template is a **new documentation instrument**, not a recovered historical screening log.

Three firms were purposively examined: Minsida (833394), Shanghai HIUV New Materials (688680), and Forstar (835640). The selection was based on available candidate narratives and inspectable patent pairs, allowing comparison of different kinds/strengths of technological-continuity evidence; **the selected cases do not measure precision, recall, or selection frequency**. The available documents do not establish non-anticipation consistently. The Forstar pair is a qualified boundary illustration rather than a confirmed technological reuse. The 2025 news sources are post-sample illustrations.

### Counts and limitations (do not impute)

| Quantity | Evidence/status |
| --- | --- |
| Annual-report corpus size quoted in the manuscript | Approximately 61,116; **historical stage and final processing count not independently verified from scripts** |
| Financial-news corpus size quoted in the manuscript | Approximately 1,127,012; **actual LLM-success count unverified** |
| Actual number of documents completed by the LLM | Not available in supplied run outputs; potentially recoverable from the original JSONL file |
| Number of LLM-flagged candidate records | Not available; can only reconstruct **a new explicitly defined flag rule**, not an undocumented historical selection rule |
| Number of candidate records manually reviewed | Original complete ledger not retained / not provided |
| Number of rejected candidates | Not available |
| Selected firm illustrations | Three firms (covering several patent pairs) |
| Formal LLM–human agreement | Not computed or claimed |
| Systematic patent–text firm-year comparison | Not performed or claimed |

`scripts/summarize_jsonl.py` can inspect an existing JSONL file and count parsed responses and simple potential positive signals. Its flag counts are **retrospective operational summaries under its own documented rule**, not the historical manual-screening count. If no JSONL file survives, actual model-completed and candidate counts cannot be certified.

## Reproducibility and known limitations

1. **Incomplete historical metadata.** The supplied scripts do not fix the DeepSeek model deployment snapshot, access dates, original Python/package versions, or original API default sampling settings. These cannot be fabricated.
2. **Partial pipeline release.** News-specific executable scripts, full collection manifests, intermediate JSONL results and original manual-review logs were not provided.
3. **Sampling ambiguity.** The annual-report selection/sampling script may not represent the full reported collection of annual reports; retain the original intermediate manifests and document the exact selection used in the submitted study.
4. **Potential source gaps.** The crawler requests one 30-record page per stock/year and does not paginate; PDF extraction has no OCR; central-window text truncation can omit relevant paragraphs.
5. **Not guaranteed JSON validity.** The repair parser does not guarantee every result satisfies the intended nested structure or is supported by the input text.
6. **Citation linkage.** Corporate narratives and patent citation pairs are not normally one-to-one matched. Index values aggregated over a focal patent's citations should not be misrepresented as a binary result for one individual pair.
7. **No population inference.** The three cases are purposive illustrations; they do not establish the accuracy of the screening framework or the prevalence of exaptation in all firms.

## Security and data rights

**Never commit API keys, access tokens, private paths, unpublished reports, proprietary company text or local run logs containing secrets.** `.gitignore` excludes common private outputs. The copies of the supplied crawler and runner were adjusted to enable TLS verification and avoid printing secret fragments or complete model responses. The author should verify the provenance and permission to redistribute the stock-ID lookup and any original documents before publishing. Requests to external providers incur service costs and are not executed when merely viewing this repository.

## Recommended citation / reporting statement

> The textual corpus was screened using a structured Chinese-language prompt with DeepSeek-R1 via the SiliconFlow API. The available scripts and prompt are deposited with a README specifying inputs, outputs, implementation parameters, and limitations. The LLM outputs served as candidate narrative signals, which were examined qualitatively against original corporate materials and patent documents using four explicit criteria. No firm-year quantitative textual validation or screening-accuracy estimate is claimed.

## Relation to released patent-based variables (outside the supplied text scripts)

The submitted study also releases patent-pair and focal-patent measures. The present GitHub package **does not contain a complete independently reproducible patent-data construction workflow**, and the Python text-analysis code does not calculate these variables. For transparency, their intended definitions and levels are listed here; authors must separately provide the exact final patent-pair builder, deduplication rules, IPC/NEIC mapping files and tested scripts to satisfy a *full-dataset* reproducibility claim.

| Variable family | Intended unit | Construction concept and caveat |
| --- | --- | --- |
| `d3`, `d4` | Patent citation pair | Binary non-match between the citing patent's main IPC class/subclass and the **set** of IPCs assigned to the cited focal patent (three / four characters); citation direction and IPC validity must be verified. |
| `Exaptation3`, `Exaptation4` | Unique cited focal patent | Mean of the respective valid pair indicators over its defined forward-citation denominator; repeated values in a pair file do **not** create independent focal patents. |
| `NEIC Distance_min`, `NEIC Distance_mean` | Patent citation pair | Respectively minimum and average hierarchical distances across mapped patent-level NEIC combinations; requires the study's verified IPC–NEIC mapping implementation, which is not present here. |
| `serendipity_innovation.*` | Text document | Structured LLM-extracted candidate signals and explanations. They are not patent-level exaptation labels. |

The final patent dataset's sample definition and identifying unit must be consistent across the manuscript, released data, and separate patent construction scripts. The textual examples must not be used to infer a pair's binary `d3`/`d4` values from its patent-level Exaptation proportions.

[README-1.md](https://github.com/user-attachments/files/34911400/README-1.md)
# AI-assisted textual screening for potential exaptive technological redeployment in Chinese listed firms

**Companion materials for:** *A patent citation dataset for studying potential exaptive technological redeployment in China*

## Scope and interpretation

This repository documents the **available** implementation of annual-report collection, text preparation, DeepSeek-R1 structured screening, and qualitative interpretation. It accompanies **Part III: AI-assisted screening and manual case review** of the study. The LLM output provided candidate firm-level narratives; patent-pair assessments required separate examination of the cited and citing patent documents. Neither the LLM labels nor cross-class IPC citations, by themselves, identify confirmed exaptation events.

The study reports a **purposively selected manual review of 34 focal-patent cases** (19 high-indicator cases and 15 low-indicator comparisons) from an initial pool of **500 candidate cases**. Among the 19 high-indicator cases, eight were classified as *concordant*, nine as *discordant*, and two as *inconclusive*. These are qualitative case-review outcomes, **not** estimates of population-level indicator accuracy or LLM precision. The complete case-level patent-text records are intended to accompany the dataset on Figshare; the Python scripts in this repository do **not** constitute a validated patent-pair classifier, a firm-year quantitative validation study, or a statistical audit of LLM performance.

The focal-patent **application-year** window in the patent study is **2000–2023**. A *later citing patent* may have a later publication date: its eligibility in the released citation-pair data depends on the study's actual citation-extraction cutoff, which must be checked. Patent documents used only as illustrations after that cutoff and corporate disclosures/news from 2025 must be identified as *post-sample contextual evidence*, not presented as focal-patent observations from 2000–2023.

**Evidence status:** This repository package was prepared from Python and prompt files supplied by the authors. No original run logs, complete JSONL results, original 500-to-34 selection ledger, or historic model-access date were supplied with that package. The case counts above are **author-reported manuscript figures**, not independently reconstructed from those scripts. This README documents observable code settings; it does not invent missing experimental totals. Before public upload, the authors must verify the actual repository contents, run provenance, documented case outcomes, rights, and data availability.

## Repository contents

```text
README.md                                Scope, actual implementation, evidence status, execution order, and limitations
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
  manual_review_template.csv              Empty review template; not the historical 34-case review ledger
docs/
  Part_III_revised.md                     Draft Part III wording (check against current manuscript)
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
| 6. Manual patent-pair review | **Human procedure, not a supplied automated script** | Candidate cases, original patent documents, model-screened corporate sources | Case-level evidence and concordant/discordant/inconclusive assessment | The manuscript reports 500 initial candidates and 34 selected cases; the selection ledger and completed case records were not supplied with these scripts. |

**Important input limitations:** `行业股票.xlsx` was **not** part of the supplied package and is required for Stages 1–3. The annual-report scripts do not establish the exact text-record totals quoted in the manuscript; the historical input/output manifests would be needed to verify those totals. A separate Sohu-financial-news crawler, merger, annotator, and export workflow were **not supplied in this package**. Consequently, the **news** pipeline cannot be reproduced end-to-end from the available scripts. Patent identification, IPC-based indices, and NEIC distances are also generated outside this textual-screening codebase.

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

## Indicator-guided manual patent-pair review

The manuscript reports that **500 candidate cases** were initially collected and **34 focal patents** were purposively selected for detailed examination: **19 high-indicator cases** and **15 low-indicator comparisons**. The low-indicator group was defined by both `IPC3_distance = 0` and `IPC4_distance = 0`. The original machine-readable selection ledger was not included among the supplied script files; accordingly, this section reports the manuscript's described procedure and counts, rather than asserting that case selection is reproducible from the released Python code alone.

For each selected focal patent, the manual assessment examined relevant cited–citing patent relationships using abstracts, claims and, where necessary, technical descriptions. The assessment distinguished three questions:

1. **Technological continuity:** Did the later patent retain an identifiable material, structure, operating principle, method, or other technical feature disclosed in the earlier patent?
2. **Functional or application change:** Was that retained content used for a different function or application rather than solely incremental improvement in the original use?
3. **Non-anticipation (recorded separately):** Did the available original-patent and supporting documents indicate that the later use lay beyond the earlier development objectives? Absence of explicit anticipation is not proof of unforeseeability.

AI-screened annual reports and financial news were used as **contextual evidence**, not as automatic validation labels. Patent documents, citation identifiers and supporting texts must be traceable to their original sources. The review used the following outcomes:

| Group | Cases | Review interpretation |
| --- | ---: | --- |
| High indicator — **concordant** | 8 | Patent-text evidence supported both identifiable technical continuity and a change in function/application. |
| High indicator — **discordant** | 9 | The reviewed relation did not satisfy both conditions; for example, it showed an improvement within the same use or merely a generic knowledge link. |
| High indicator — **inconclusive** | 2 | Available patent texts were insufficient to determine whether specific technical content was retained and redeployed. |
| **Low-indicator comparison** | 15 | Both focal-patent IPC shares equalled zero; the same manual criteria were applied to the selected comparison cases. |
| **Total** | **34** | Purposively selected cases; not a representative random sample. |

The four representative patent pairs discussed in the manuscript illustrate a high-indicator concordant case (ArcSoft, 688088), a high-indicator discordant case (Maider Medical, **688310**), an inconclusive case (Monte Bianco, **836807**) and a low-indicator comparison (Sinopep, 688076). The fuller 34-case descriptions are intended for the accompanying **Figshare** materials; the present repository should not claim to contain them unless those files are actually deposited.

For reproducibility, each completed review record should retain the focal and citing patent publication/application identifiers, firm and stock code, focal-level indicators, source document URL or stable ID, publication date, relevant claims or description locations, technical comparison, and manual outcome. `templates/manual_review_template.csv` is an **empty documentation template**, not a recovered historical screening log. It cannot substitute for the original completed 34-case records.

### Counts and limitations (do not impute)

| Quantity | Evidence/status |
| --- | --- |
| Annual-report corpus size quoted in the manuscript | Approximately 61,116; **historical stage and final processing count not independently verified from scripts** |
| Financial-news corpus size quoted in the manuscript | Approximately 1,127,012; **actual LLM-success count unverified** |
| Actual number of documents completed by the LLM | Not available in supplied run outputs; potentially recoverable from the original JSONL file |
| Number of LLM-flagged candidate records | Not available; can only reconstruct **a new explicitly defined flag rule**, not an undocumented historical selection rule |
| Initial candidate cases reported by the manuscript | **500**, author-reported; candidate-generation and selection manifest not independently available in supplied scripts |
| Focal-patent cases selected for manual review | **34**: 19 high-indicator, 15 low-indicator; author-reported, detailed records intended for Figshare |
| High-indicator manual outcomes | **8 concordant, 9 discordant, 2 inconclusive**; purposively selected cases, not sample-wide validation rates |
| Number of rejected candidates | Not available |
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
7. **No population inference.** The 34 purposively selected cases and their manual outcomes do not estimate the predictive accuracy of the IPC indicators, the accuracy of the LLM, or the prevalence of exaptation across the dataset.
8. **Sample-period boundaries.** The 2000–2023 restriction concerns the **focal patent's application year**, not automatically every citing patent's publication date. Check each citing patent against the actual extraction cutoff. Identify 2025 business reports and genuinely out-of-sample patent illustrations separately.

## Security and data rights

**Never commit API keys, access tokens, private paths, unpublished reports, proprietary company text or local run logs containing secrets.** `.gitignore` excludes common private outputs. The copies of the supplied crawler and runner were adjusted to enable TLS verification and avoid printing secret fragments or complete model responses. The author should verify the provenance and permission to redistribute the stock-ID lookup and any original documents before publishing. Requests to external providers incur service costs and are not executed when merely viewing this repository.

## Data provenance and sharing constraints

For the released patent-pair dataset, retain the **cited and citing patent publication/application identifiers** and the originating patent-data source so that each citation relationship is traceable. For document-derived observations, retain **record-level source information** wherever possible (for example, annual-report issuer, reporting year, document URL or persistent identifier; financial-news title, publisher, date and original URL). A separate bibliography alone is insufficient to link individual extracted observations to their sources.

Share extracted variables, metadata, short necessary evidence descriptions and review decisions subject to the applicable licence. **Do not redistribute complete copyrighted annual reports, full news articles or original figures without an appropriate licence or permission.** Review the rights associated with the CNINFO records, Sohu news, patent data and stock-ID lookup before publication. A value such as `serendipity_innovation = "none"` means that screening did not retrieve a relevant narrative; it **does not** prove that an unexpected innovation event was impossible.

## Suggested manuscript reporting statement

> Corporate annual reports and financial news were screened for candidate narratives of potential technological redeployment using a structured Chinese-language prompt and DeepSeek-R1 accessed through the SiliconFlow API. The available annual-report processing and screening scripts, the prompt, input/output requirements and known limitations are documented in the accompanying repository. The LLM outputs served as contextual screening information; selected cited–citing patent relationships were subsequently examined manually for identifiable technological continuity and a change in function or application, with available evidence concerning non-anticipation recorded separately. The purposively selected 34-case review provides qualitative examples and does not establish population-level indicator accuracy or LLM classification performance.

## Relation to released patent-based data (outside the supplied text scripts)

The manuscript reports **718 Chinese listed firms**, **41,017 unique focal patents** and **185,749 cited–citing patent-pair observations** in the final forward-citation dataset. The cross-framework backward-citation benchmarking subset comprises **36,550 focal patents**, reflecting missing or unmatched backward-citation information for some firms. These figures are manuscript-reported and **cannot be verified from the text-screening scripts alone**.

The study also releases patent-pair and focal-patent measures. This GitHub package **does not contain a complete independently reproducible patent-data construction workflow**, and the Python text-analysis code does not calculate these variables. Authors must separately supply or reference the final citation-pair builder, deduplication rules, IPC/NEIC crosswalk, source manifests and tested scripts if claiming full patent-data reproducibility. All nomenclature and record counts should be checked against the final Figshare dataset.

| Variable family | Intended unit | Construction concept and caveat |
| --- | --- | --- |
| `d3`, `d4` | Patent citation pair | **Binary IPC-based cross-class forward-citation indicators** at the three-character class and four-character subclass levels. A pair qualifies when the later citing patent's main IPC does not match any IPC code in the earlier focal patent's assigned-code set at the respective level. Missing classification information must not be silently treated as zero. |
| `IPC3_distance`, `IPC4_distance` | Unique earlier (cited) focal patent | **Shares of qualifying forward citations**, calculated from valid pair-level `d3` and `d4` values. These are proxies for **potential** exaptive technological redeployment, not direct labels of confirmed exaptation. Values repeated across a pair file do not create independent patents. |
| Pair-level NEIC minimum / mean distance | Patent citation pair | Minimum and arithmetic mean hierarchical distances across valid NEIC-code combinations mapped from the two patents' IPC classifications (range 0–3). Exact exported variable names should be checked against Figshare data. |
| Focal-level NEIC minimum / mean distance | Unique earlier (cited) focal patent | Averages of the respective valid pair-level NEIC distances across a focal patent's eligible forward citations. |
| `serendipity_innovation.*` | Text document | Structured LLM-extracted candidate signals and explanations. They are not patent-level exaptation labels. |

The final patent dataset's sample definition and identifying unit must be consistent across the manuscript, released data, and separate patent construction scripts. A pair's binary `d3`/`d4` value **cannot** be inferred from a focal patent's aggregate `IPC3_distance`/`IPC4_distance` share. Keep pair-level indicators, focal-level measures and manually reviewed case outcomes distinct.

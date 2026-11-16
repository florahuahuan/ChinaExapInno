AI-assisted textual screening for potential exaptive technological redeployment in Chinese listed firms

Scope and interpretation

This repository accompanies the textual-methods component of the study A patent citation dataset for studying potential exaptive technological redeployment in China. As stated in the manuscript, the custom Python scripts are provided to document textual data collection, preprocessing, and AI-assisted screening of Chinese listed firms' annual reports and financial news. 

The available code documents the annual-report workflow, including CNINFO metadata collection, PDF downloading, text extraction, and structured screening using DeepSeek-R1 through SiliconFlow. 

AI-generated results are candidate textual signals for qualitative examination, not independently verified exaptation events or quantitative validation of patent indicators. The distinction between implemented scripts, reported research procedures, and unavailable historical records is maintained throughout.

Repository contents

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

The scripts in scripts/ are publication-oriented copies of the supplied files. Security-only adjustments were made to the API runner and announcement crawler (TLS certificate verification enabled; API URL switched to HTTPS; API-key fragments and full server response are no longer printed in logs). They retain the original study's prompt, model identifier, conceptual extraction, token window, thread count and output record structure. 

Textual data sources and processing workflow

The textual sources comprise (1) annual reports obtained through CNINFO and (2) financial news described in the study as sourced from Sohu Stock News. The executable stages below describe the annual-report pipeline supplied in this repository. 

Available annual-report pipeline

StageScriptInputsOutputsImplementation notes1. Annual-report metadatascripts/00_crawl_annual_reports.py行业股票.xlsx, data/szse_stock.json (place beside script or adjust path), CNINFO endpoint年报.csvLoops over requested years 2001–2024. Uses page size 30 but does not explicitly paginate additional results; check completeness.2. Clean and samplescripts/01_clean_annual_reports.py年报.csv, 行业股票.xlsx年报清洗.xlsx, 统计结果.xlsx, 随机选取30个股票.xlsx, 最终整理年报.xlsxKeeps latest announcement per firm/calendar year; firms with at least 10 such records eligible; samples 30 firms per board with numpy.random.seed(1). This is not proof that all initially collected reports were LLM-processed.3. PDF downloadscripts/02_download_annual_report_pdfs.py最终整理年报.xlsxpdfs/<board>/<code>_<firm>_<reportyear>.pdfUses 10 workers and extracts the report year from title.4. PDF-to-TXTscripts/03_extract_pdf_text.pypdfs/*/*.pdftxts/<board>/<file>.txtUses pdfplumber, 10 workers. Text must be extractable; scanned/image-only pages are not OCR-processed.5. Structured LLM extractionscripts/04_run_deepseek_extraction.py with scripts/prompt.py and scripts/format_to_json.pyA glob of TXT files and API credentials via environment variablelabel_jsons/deepseek_results.jsonlDefaults and exact JSONL fields below. Resumes by doc_id; failures may not appear in the output.6. Manual case reviewHuman procedure, not a supplied automated scriptOriginal documents, model outputs, patent texts/claimsCompleted review log / case narrativesSee four criteria and template below. Historical complete case-count ledger was not provided.

News-workflow and input limitations: The annual-report scripts do not establish the exact text-record totals stated in the manuscript; a complete execution manifest must be reconstructed from actual input/output files. The separate Sohu-news crawler, merger, LLM annotator and export scripts described in the authors' earlier documentation were not supplied in this package. 

Software environment and installation

The original Python version is 3.13. requirements.txt lists the package names imported by the supplied code; it is not a historically pinned environment. 

Suggested setup for a new test environment (not proof of the historical environment):

python -m venv .venv
# Activate .venv for your operating system, then:
python -m pip install -r requirements.txt

The scripts were designed around local folders and input files. Set working directories and input paths as appropriate; changing path configuration does not change the coding framework.

Model and prompt configuration: settings visible in the supplied code

ItemValue / qualificationAPI providerSiliconFlow (https://api.siliconflow.cn/v1 in the publication-safe copy)Default model IDdeepseek-ai/DeepSeek-R1 (overridable through OPENAI_MODEL)Model access dateOctober 1, 2025 (via the SiliconFlow API)Immutable model build or version snapshotNot available in supplied scriptsHistorical temperature and top-pNot explicitly set in the request payload; effective provider defaults not recordedActual system messageFull PROMPT string from scripts/prompt.pyActual user messageText extracted from one selected annual-report TXT fileToken countingtiktoken encoding o200k_base (a budgeting approximation, not necessarily the provider's exact tokenizer)MAX_DOC_TOKENS80,000 by defaultPROMPT_HEADROOM1,024 by defaultMIN_WINDOW_TOKENS1,500 by defaultLong-text operationKeeps a central contiguous text segment, not the full beginning and end and not chunk-by-chunk coverageParallelismFive request workers (ThreadPoolExecutor(max_workers=5))Generation payloadModel, system/user messages, stream: false; no explicit JSON schema or response_format enforcementJSON handlingformat_to_json.py attempts direct parsing, wrapper removal, first-object extraction and json_repair; does not independently verify schema semanticsOutputAppend-only JSON Lines at label_jsons/deepseek_results.jsonl by default

To run the LLM processing stage from the repository root, an example is:

export OPENAI_API_KEY="<YOUR_PRIVATE_KEY>"   # set privately; do not commit
export MD_GLOB="/path/to/your/txts/**/*.txt"
export SAVE_DIR="label_jsons"
export RESULT_FILE="label_jsons/deepseek_results.jsonl"
# prompt.py and format_to_json.py reside beside the runner:
python scripts/04_run_deepseek_extraction.py

When running on Windows, use the appropriate command-shell syntax for environment variables. The runner's historical default MD_GLOB was a local Windows path and will not work unchanged on another computer. A doc_id is currently derived from the file basename, which may collide if folders contain identically named files; verify uniqueness and, if needed, change the public execution setup with the change documented. The existing output also skips records with previously seen doc_id values; a new clean test run should use a new result file.

Record-level output schema

Each JSONL line has the outer structure:

{"doc_id":"example.txt","md_path":"/path/example.txt","response":{"serendipity_innovation":{"迹象":{"结果":"有","说明":"..."}}}}

The original prompt.py is authoritative for the complete Chinese-language nested output shape. Core branches include:

Output branch
Interpretation
serendipity_innovation.迹象
Overall textual serendipity-related signal and explanation
serendipity_innovation.识别维度.非预期性
Non-anticipation and explanation
serendipity_innovation.识别维度.机会识别
Opportunity recognition and explanation
serendipity_innovation.识别维度.商业价值转化
Commercial value and explanation
serendipity_innovation.技术或功能转移
Technological or functional transfer and explanation
serendipity_innovation.是否偶然发现
Accidental discovery and explanation
serendipity_innovation.关键词
Keywords as cues, not proof
serendipity_innovation.案例, 涉及技术, 技术类型, 研发投入背景, 战略一致性, 市场转化, 可能原因
Context and explanatory fields

A validly parsed JSON object is not necessarily a valid evidence-backed judgment. The prompt includes predefined example-shaped case fields and keywords. Source quotations, pages and evidence locations must be checked manually rather than assumed to have been extracted reliably.

Coding framework: six analytical dimensions

Dimension
Operational question
Needed corroborating information
Overall signal
Does the text contain a candidate narrative associated with technological redeployment or serendipity?
Source-supported description, not just a model-generated label
Non-anticipation
Is the later application absent from, or inconsistent with, the original goal?
Initial objectives contrasted with later outcomes
Opportunity recognition
Was an additional use or opportunity identified?
Documentary account of recognition, not merely market presence
Commercial value
Was an actual economic or commercial result reported?
Products, deployments, customers or contracts; distinguish plans from outcomes
Technological/functional transfer
Is an underlying technology retained and put to a different use?
Technical-content continuity and changed application/function
Accidental discovery
Was the use discovered unexpectedly?
Direct narrative evidence; not inferred from IPC differences

Keywords are retrieval cues, not necessary or sufficient criteria for exaptation. 

Qualitative review and illustrative case selection

Four author-provided review criteria were applied conceptually:

Identify the original technology and its initial application.Establish evidence of a later change of function or application.Examine continuity in underlying technical content.Assess available evidence regarding whether the later application was non-anticipated.

Researchers should preserve supporting document identifier, URL/filename, date, page or paragraph, patent number, claim/description location, and a decision with an explanatory limitation in templates/manual_review_template.csv. 

Three firms were purposively examined: Minsida (833394), Shanghai HIUV New Materials (688680), and Forstar (835640). The selection was based on available candidate narratives and inspectable patent pairs, allowing comparison of different kinds/strengths of technological-continuity evidence; the selected cases do not measure precision, recall, or selection frequency. 

Reproducibility and known limitations

Incomplete historical metadata. The supplied scripts do not fix the DeepSeek model deployment snapshot, original Python/package versions, or original API default sampling settings. These cannot be fabricated.Partial pipeline release. News-specific executable scripts, full collection manifests, intermediate JSONL results and original manual-review logs were not provided.The crawler requests one 30-record page per stock/year and does not paginate; PDF extraction has no OCR; central-window text truncation can omit relevant paragraphs.Not guaranteed JSON validity. The repair parser does not guarantee every result satisfies the intended nested structure or is supported by the input text.Citation linkage. Text-document observations are distinct from patent observations. Do not interpret an AI-generated narrative flag as a patent-level classification or as validation of a patent indicator.

Security and data rights

Never commit API keys, access tokens, private paths, unpublished reports, proprietary company text or local run logs containing secrets. .gitignore excludes common private outputs. The copies of the supplied crawler and runner were adjusted to enable TLS verification and avoid printing secret fragments or complete model responses. The author should verify the provenance and permission to redistribute the stock-ID lookup and any original documents before publishing. Requests to external providers incur service costs and are not executed when merely viewing this repository.

Suggested manuscript reporting statement

Annual reports and financial news were used as textual sources for AI-assisted screening of candidate narratives. A structured Chinese-language prompt was applied with DeepSeek-R1 through the SiliconFlow API (model access date: October 1, 2025). The repository provides the available annual-report processing and screening scripts, prompt, input/output descriptions, and implementation notes; the news-specific scripts are not included. Candidate textual signals were examined qualitatively using explicit review criteria. 

Relationship to the manuscript and data scope

The manuscript cites this GitHub repository specifically for the custom Python scripts used in textual data collection, preprocessing, and AI-assisted screening. The scripts here process text documents and produce document-level structured candidate signals. They do not construct the study's quantitative patent dataset or its patent-based indicators.

The annual-report and financial-news corpora are textual sources for contextual qualitative examination. They are separate from the patent citation records analyzed elsewhere in the study. 

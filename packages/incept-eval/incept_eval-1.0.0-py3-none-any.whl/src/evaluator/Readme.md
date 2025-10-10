# Evaluator

## Directory Structure

```
evaluator/
├── scripts/              # Utility scripts for analysis and reporting
│   ├── benchmark_report.py         # Generate comprehensive benchmark reports
│   ├── delete_low_scores.py        # Analyze and delete low-scoring questions
│   └── generate_jsonl_report.py    # Generate reports from JSONL evaluation runs
│
├── reports/              # Generated benchmark and evaluation reports
│   ├── incept_benchmark_report.md      # Main benchmark report (Markdown)
│   ├── incept_benchmark_report.json    # Main benchmark report (JSON)
│   └── evaluation_*_report.*           # Specific evaluation run reports
│
├── output/               # Evaluation run outputs
│   └── evaluation_runs/             # Raw evaluation JSONL files
│       └── MM_DD_YYYY/              # Organized by date
│
├── archive/              # Archived data and historical records
│   └── low_scores_deleted.json      # Record of deleted low-scoring questions
│
├── runs/                 # Evaluation interpreters and legacy scripts
│   ├── interpreter.py               # Original evaluation interpreter
│   └── interpreter_v2.py            # Database-based evaluation interpreter
│
└── EduBench/             # EduBench evaluation framework (submodule)
```

## EduBench Framework

We use the official [EduBench](https://github.com/StanHus/EduBench) framework (git submodule at `EduBench/`) for objective educational quality evaluation. EduBench is a peer-reviewed benchmark (arXiv:2505.16160) with 9 educational scenarios and 12 evaluation metrics.

### What is EduBench?

EduBench evaluates educational content across three core dimensions:
1. **Scenario Adaptability** - contextual appropriateness and task completion
2. **Factual & Reasoning Accuracy** - correctness and logical rigor
3. **Pedagogical Application** - teaching effectiveness and learning support

It defines 9 educational scenarios (QA, EC, IP, PLS, ES, QG, AG, TMG, PCC) and 12 quality metrics (BFA, DKA, RPR, EICP, CSI, MGP, PAS, HOTS, IFTC, RTC, CRSC, SEI).

### How We Use EduBench

**1. Direct code imports:**
```python
# edubench.py lines 14-19, 291
from src.evaluator.EduBench.code.evaluation.evaluation import TASK_PROMPT_TEMPLATES

# Use official prompts exactly as defined
prompt = TASK_PROMPT_TEMPLATES["QA"](question_text)
```

**2. Official evaluation model:**
- All questions evaluated by **EDU-Qwen2.5-7B** (HuggingFace endpoint)
- Same model used by EduBench paper for consistency
- See: https://huggingface.co/DirectionAI/EDU-Qwen2.5-7B

**3. Three core tasks** (from EduBench's 9 scenarios):
- **QA (Question Answering)**: Student answers question → model checks if correct
  - **Tests:** Basic Factual Accuracy (BFA), Domain Knowledge Accuracy (DKA)
  - **Measures:** Can the model identify the right answer? (factual correctness)
  - **Weight:** 35%

- **EC (Error Correction)**: Student gives wrong answer → model corrects with explanation
  - **Tests:** Error Identification & Correction Precision (EICP), Clarity & Simplicity (CSI)
  - **Measures:** Can the model correct errors pedagogically? (curriculum alignment)
  - **Weight:** 45% (highest - curriculum compliance is critical)

- **IP (Idea Provision)**: Student needs help → model provides step-by-step approach
  - **Tests:** Reasoning Process Rigor (RPR), Higher-Order Thinking Skills (HOTS)
  - **Measures:** Can the model scaffold learning? (reasoning depth)
  - **Weight:** 20%

**4. Scoring methodology:**
```python
# Our scoring (interpreter.py) based on EduBench rubrics:
# - QA: Exact match with gold answer = 10.0, else 0.0
# - EC: Correct correction + explanation = 8.0, else 2.0
# - IP: Complete steps = 10.0, final answer only = 8.0, else 0.0

# Weighted average (interpreter_v2.py:289-294):
weighted_score = (QA × 0.35) + (EC × 0.45) + (IP × 0.20)
```

**5. What we added:**
- Database integration (PostgreSQL storage)
- Batch processing (parallel evaluation of 60 questions)
- HuggingFace API interface for EDU-Qwen2.5-7B
- Analysis pipeline (`interpreter_v2.py`, `benchmark_report.py`)

### Why These Specific Tasks?

We focus on **3 student-oriented tasks** (QA, EC, IP) from EduBench's 9 scenarios because:
- Most relevant for assessing **question quality**
- Teacher-oriented tasks (QG, AG, TMG, PCC) test content generation, not question evaluation
- Support tasks (PLS, ES) test tutoring capabilities, not question validity

### Verification

**Proof of authentic EduBench usage:**
1. Git submodule: `git submodule status EduBench/`
2. Direct imports: `grep -r "TASK_PROMPT_TEMPLATES" edubench.py batch_edubench.py`
3. Model calls: HuggingFace endpoint for EDU-Qwen2.5-7B (see `query_hf_model()` in `edubench.py:25-69`)
4. Database storage: `evaluation_edubench` column contains official task responses

### Run Evaluation

```bash
# Evaluate recent questions
python src/evaluator/edubench.py --db_limit 100 --db_grade 3 --db_hours 168

# Production batch processing (continuous)
POSTGRES_URI="..." python src/evaluator/batch_edubench.py
```

**Parameters:**
- `--db_limit`: Max questions to evaluate
- `--db_grade`: Grade filter (3-12)
- `--db_subject`: Subject filter
- `--db_hours`: Hours ago (default: 168 = 1 week)

### Quality Threshold

Questions scoring **< 8.0/10.0** weighted average are filtered out. Only validated, curriculum-aligned questions reach production.

**References:**
- EduBench paper: https://arxiv.org/pdf/2505.16160
- EduBench model: https://huggingface.co/DirectionAI/EDU-Qwen2.5-7B
- Our fork: https://github.com/StanHus/EduBench (submodule at `EduBench/`)

## Key Scripts

### 1. benchmark_report.py

Generate comprehensive benchmark reports from the database.

**Usage:**
```bash
POSTGRES_URI="..." python scripts/benchmark_report.py \
  --start-date 2025-09-30 \
  --end-date 2025-10-02 \
  --output-md reports/benchmark.md \
  --output-json reports/benchmark.json
```

**Features:**
- Query orchestrator-pipeline questions from database
- Calculate weighted scores using proper formula
- Generate per-grade performance breakdowns
- Export comprehensive markdown and JSON reports
- Filter by date range and model

### 2. delete_low_scores.py

Analyze question scores and remove low-performing questions from the database.

**Usage:**
```bash
POSTGRES_URI="..." python scripts/delete_low_scores.py \
  --threshold 8.0 \
  --delete \
  --confirm \
  --export deleted_questions.json
```

**Features:**
- Analyze score distribution across all questions
- Filter by quality threshold (default: 8.0/10.0)
- Preview deletion candidates (dry-run mode)
- Export deleted questions for record-keeping
- Breakdown by grade and model

### 3. generate_jsonl_report.py

Generate detailed reports from JSONL evaluation run files.

**Usage:**
```bash
python scripts/generate_jsonl_report.py \
  output/evaluation_runs/07_10_2025/13-01-37.jsonl \
  --output-md reports/eval_report.md \
  --output-json reports/eval_report.json
```

**Features:**
- Parse JSONL evaluation outputs
- Calculate weighted scores using proper formula
- Generate per-grade and per-subject breakdowns
- Provide quality assessment (PASS/BELOW THRESHOLD)
- Export detailed markdown and JSON reports

### 4. interpreter_v2.py

Database-based evaluation interpreter for orchestrator-pipeline questions.

**Usage:**
```bash
# View all evaluated questions
POSTGRES_URI="..." python runs/interpreter_v2.py

# Filter by grade with date range
POSTGRES_URI="..." python runs/interpreter_v2.py \
  --grade 5 \
  --start-date 2025-09-30 \
  --end-date 2025-10-02 \
  --detailed
```

Available parameters:
- `--grade`: Filter by grade level
- `--subject`: Filter by subject
- `--language`: Filter by language (ar, en)
- `--start-date`: Filter by start date (YYYY-MM-DD)
- `--end-date`: Filter by end date (YYYY-MM-DD)
- `--limit`: Maximum questions to analyze
- `--detailed`: Show detailed statistics
- `--output`: Export to JSON file

## Workflow

### 1. Run Evaluations

```bash
# Run EduBench evaluation on recent questions
python edubench.py --db_limit 300 --db_grade 3 --db_hours 720
```

### 2. Analyze Results

```bash
# Interpret JSONL results
python scripts/generate_jsonl_report.py \
  output/evaluation_runs/MM_DD_YYYY/HH-MM-SS.jsonl
```

### 3. Clean Low-Quality Questions

```bash
# Remove questions below threshold (dry-run first)
POSTGRES_URI="..." python scripts/delete_low_scores.py --threshold 8.0

# Actually delete after review
POSTGRES_URI="..." python scripts/delete_low_scores.py \
  --threshold 8.0 --delete --confirm --export archive/deleted.json
```

### 4. Generate Benchmark Reports

```bash
# Create comprehensive benchmark report
POSTGRES_URI="..." python scripts/benchmark_report.py \
  --start-date 2025-09-30 \
  --end-date 2025-10-02 \
  --output-md reports/incept_benchmark_report.md \
  --output-json reports/incept_benchmark_report.json
```

## Prompt Engineering Benchmarks

Located in `src/prompt_engineering/`, these provide baseline comparisons for our orchestrator pipeline.

### Falcon Benchmark (`falcon/main.py`)

Uses Falcon-180B with direct prompt engineering. Requests 5 questions per call with parallel generation (5 workers). This small batch size ensures maximum quality per request while maintaining throughput.

```bash
python src/prompt_engineering/falcon/main.py
```

### OpenAI Benchmark (`openai/main.py`)

Uses GPT-4 with direct prompt engineering. Requests 10 questions per call with parallel generation (10 workers). Similar batch strategy prioritizes quality over bulk generation.

```bash
python src/prompt_engineering/openai/main.py
```

### Why These Are Strong Benchmarks

These implementations represent the upper bound of what pure prompt engineering can achieve:
- **Small batch requests** (5-10 questions): Prevents quality degradation from large batch processing
- **Parallel execution**: Multiple concurrent requests maximize throughput without compromising quality
- **Frontier models**: GPT-4 and Falcon-180B are among the most capable models for Arabic educational content
- **Direct prompting**: No intermediate steps or complexity—just optimal prompts to the best models

This configuration ensures our orchestrator pipeline is compared against the best possible prompt-engineering baseline, not a suboptimal implementation.

## Database Schema

Questions are stored in the `uae_educational_questions_cleaned_duplicate` table:

**Key Fields:**
- `id`: Unique question identifier
- `normalized_grade`: Grade level (3, 5, 8, 9, 12)
- `subject_area`: Subject (Mathematics, Science, etc.)
- `language`: Language code (ar, en)
- `evaluation_edubench`: JSON evaluation results
- `extracted_by_model`: Model used for generation
- `created_at`: Timestamp

## Environment Variables

```bash
# Required for database operations
export POSTGRES_URI="postgresql://user:password@host:port/database"

# Optional: HuggingFace API token for model inference
export HF_TOKEN="your_token_here"
```

## Contributing

When adding new scripts or reports:
1. Place utility scripts in `scripts/`
2. Save generated reports in `reports/`
3. Store evaluation runs in `output/evaluation_runs/MM_DD_YYYY/`
4. Archive historical data in `archive/`
5. Update this README with usage instructions

---

*Last Updated: October 7, 2025*

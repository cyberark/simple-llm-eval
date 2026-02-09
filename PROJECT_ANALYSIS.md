# Simpleval Project Analysis

## Project Overview

**simpleval** (Simple LLM Evaluation) is a Python framework by CyberArk for evaluating Large Language Models using the **"LLM as a Judge"** technique. It provides a CLI tool to run evaluations, compare results, and generate reports.

---

## Core Purpose

The framework solves a fundamental challenge in LLM development: **How do you systematically evaluate the quality of LLM outputs?**

The solution uses LLMs themselves as judges to assess outputs against various quality metrics (correctness, coherence, relevance, etc.). This allows for automated, scalable evaluation without requiring human reviewers for every test case.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLI (simpleval)                                │
│                     main.py → cli_args.py → Commands                        │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────────────┐
        ▼                        ▼                                ▼
┌───────────────┐    ┌───────────────────┐           ┌────────────────────┐
│  init_command │    │   run_command     │           │     reporting      │
│   (Setup)     │    │   (Execution)     │           │ (eval/compare/     │
│               │    │                   │           │  summarize)        │
└───────────────┘    └─────────┬─────────┘           └────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌───────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ llm_task_runner│    │  eval_runner    │    │  parallel_runner │
│ (Run LLM task) │    │  (Run judges)   │    │  (Concurrency)   │
└───────────────┘    └────────┬────────┘    └─────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
     ┌────────────────┐             ┌─────────────────┐
     │    Judges      │             │    Metrics      │
     │  (Providers)   │────────────▶│  (Prompts)      │
     └────────────────┘             └─────────────────┘
```

---

## Key Components

### 1. **CLI Layer** (`simpleval/main.py`, `cli_args.py`)

The entry point that exposes commands:
- `simpleval init` - Interactive setup wizard
- `simpleval run` - Execute evaluations
- `simpleval report` - Generate reports (eval, compare, summarize)
- `simpleval list-models` - Show available judge models
- `simpleval metrics-explorer` - Explore available metrics

### 2. **Evaluation Engine** (`simpleval/evaluation/`)

The core evaluation logic:

#### **Eval Runner** (`eval_runner.py`)
Orchestrates the evaluation process:
1. Loads the evaluation configuration
2. Retrieves ground truth data
3. Gets LLM task results
4. Runs judges in parallel against each metric
5. Writes results to files

#### **Judges** (`judges/`)

Judges are LLM providers that evaluate outputs. The architecture uses a **provider pattern**:

```
BaseJudge (Abstract)
    │
    ├── anthropic/judge.py      (Claude via Anthropic API)
    ├── azure/judge.py          (Azure OpenAI)
    ├── bedrock_claude_sonnet/  (AWS Bedrock Claude)
    ├── gemini/judge.py         (Google Gemini API)
    ├── generic_bedrock/        (Generic AWS Bedrock)
    ├── litellm_structured_output/ (Any LiteLLM provider)
    ├── open_ai/judge.py        (OpenAI)
    └── vertex_ai/judge.py      (Google Vertex AI)
```

`JudgeProvider` acts as a factory to instantiate the appropriate judge based on configuration.

#### **Metrics** (`metrics/`)

Metrics define what aspects to evaluate:

| Metric | Purpose |
|--------|---------|
| `correctness` | Is the answer factually correct? |
| `coherence` | Is the response logically consistent? |
| `completeness` | Does it fully answer the question? |
| `relevance` | Is it relevant to the prompt? |
| `helpfulness` | Is it useful to the user? |
| `readability` | Is it easy to understand? |
| `faithfulness` | Does it accurately reflect source material? |
| `following_instructions` | Does it follow given instructions? |

Each metric is implemented as a class inheriting from `EvaluationMetric`:

```python
class EvaluationMetric(ABC):
    @property
    def eval_prompt(self) -> str:  # The judge prompt template
    @property
    def possible_responses(self) -> List[str]:  # Valid responses
    @property
    def parser(self) -> Callable:  # Output parser
```

### 3. **Data Model** (Eval Sets & Testcases)

The framework uses a hierarchical structure:

```
eval-set-name/
├── ground_truth.jsonl      # Test cases with expected outputs
├── config.json             # Evaluation configuration
└── testcases/
    ├── testcase-1/
    │   ├── task_handler.py   # Your LLM task implementation
    │   └── llm_task_results.jsonl  # Generated results
    └── testcase-2/
        └── ...
```

- **Eval Set**: A use case you want to evaluate (e.g., "question answering")
- **Testcase**: A specific configuration variant (e.g., "gpt-4-prompt-v1" vs "claude-prompt-v2")
- **Ground Truth**: Expected inputs/outputs for comparison

### 4. **Reporting** (`commands/reporting/`)

Three report types:
1. **Eval Report** - Detailed results for a single testcase
2. **Compare Report** - Side-by-side comparison of multiple testcases
3. **Summary Report** - Aggregated metrics across evaluations

Reports can be output to console or HTML (using a React frontend in `reports-frontend/`).

### 5. **Parallel Runner** (`parallel_runner/`)

Handles concurrent execution of LLM tasks and judge evaluations using Python's threading/async capabilities with configurable concurrency limits.

---

## Data Flow

```
1. User creates eval set with ground_truth.jsonl
                    ↓
2. User implements task_handler.py (the LLM logic to test)
                    ↓
3. `simpleval run --stage task` executes LLM tasks
   → Generates llm_task_results.jsonl
                    ↓
4. `simpleval run --stage eval` runs judges
   → Judge LLM evaluates each result against metrics
   → Generates eval_results.jsonl
                    ↓
5. `simpleval report` generates human-readable reports
```

---

## Configuration

The `config.json` in each eval set controls:
- Which judge to use (`llm_as_a_judge_name`)
- Which model ID (`llm_as_a_judge_model_id`)
- Which metrics to evaluate (`eval_metrics`)
- Concurrency settings

---

## Key Design Decisions

1. **Pluggable Judges**: Easy to add new LLM providers by implementing `BaseJudge`
2. **Modular Metrics**: Metrics are separate from judges, allowing reuse
3. **Incremental Evaluation**: Only re-evaluates what's missing
4. **Parallel Execution**: Configurable concurrency for scalability
5. **Structured Output Parsing**: Uses XML or structured output for reliable judge responses

---

## Project Structure Summary

### Core Files
- **README.md** — Project overview and quick links
- **pyproject.toml** — Python project configuration (uses hatchling, Python ≥3.11)
- **requirements.txt** — Python dependencies
- **mkdocs.yml** — Documentation configuration (MkDocs Material)

### Main Directories
- **simpleval/** — Main Python package (source code)
- **tests/** — Test suite (unit and integration)
- **docs/** — Documentation (MkDocs)
- **reports-frontend/** — React/Vite frontend for HTML reports
- **simpleval/eval_sets/** — Example evaluation sets

### Key Dependencies
- **litellm** — Multi-provider LLM support
- **pydantic** — Data validation
- **click** — CLI framework
- **boto3** — AWS SDK (for Bedrock)
- **google-genai** — Google Gemini API
- **tenacity** — Retry logic
- **tqdm** — Progress bars

---

This architecture makes it straightforward to evaluate any LLM task across multiple configurations and metrics, with support for the major cloud LLM providers.

# Project Overview: Simple LLM Evaluation (simpleval)

**simpleval** is a Python CLI framework developed by CyberArk for evaluating Large Language Models (LLMs) using the **"LLM as a Judge"** technique. The core idea is to use one LLM to evaluate the outputs of another LLM against defined metrics.

**Repository:** https://github.com/cyberark/simple-llm-eval  
**Version:** 1.1.1  
**Python:** >=3.11

---

## Architecture Overview

The project follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI (main.py)                           │
│         Click-based interface with multiple commands            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Commands Layer                             │
│  run, init, compare, eval-report, summarize, explorers, etc.   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Evaluation Engine                            │
│              eval_runner.py / llm_task_runner.py               │
└─────────────────────────────────────────────────────────────────┘
              │                                    │
              ▼                                    ▼
┌──────────────────────────┐       ┌──────────────────────────────┐
│        Judges            │       │          Metrics             │
│  (LLM providers that     │       │   (Evaluation criteria:      │
│   perform evaluation)    │       │    correctness, relevance,   │
│                          │       │    completeness, etc.)       │
│  • OpenAI                │       │                              │
│  • Anthropic Claude      │       │  Each metric uses parsers    │
│  • AWS Bedrock           │       │  (XML, structured output)    │
│  • Google Gemini/Vertex  │       │  to extract scores           │
│  • Azure                 │       │                              │
│  • LiteLLM (generic)     │       └──────────────────────────────┘
└──────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Reporting System                             │
│         Console output + HTML reports (React frontend)          │
│         Compare runs, summarize testcases                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Components

### 1. CLI Entry Point (`simpleval/main.py`)

The main interface using Click. Available commands:

- `run` - Execute an evaluation
- `init` / `init-from-template` - Set up new evaluation projects
- `compare` / `compare-files` - Compare two evaluation runs
- `eval-report` / `eval-report-file` - Generate evaluation reports
- `summarize` - Summarize all testcases
- `*-explorer` commands - Explore available judges, metrics, models

### 2. Evaluation Engine (`simpleval/evaluation/`)

The core execution system:

- **`eval_runner.py`** - Orchestrates the evaluation process
- **`llm_task_runner.py`** - Handles individual LLM task execution
- **`parallel_runner/`** - Enables concurrent evaluation for performance

### 3. Judges (`simpleval/evaluation/judges/`)

Judges are the LLM providers that perform the actual evaluation. Each judge:

- Extends `BaseJudge` abstract class
- Connects to a specific LLM provider
- Returns evaluation results

Supported providers:

| Judge | Provider |
|-------|----------|
| `open_ai` | OpenAI GPT models |
| `anthropic` | Anthropic Claude |
| `bedrock_claude_sonnet` | AWS Bedrock Claude |
| `generic_bedrock` | Any AWS Bedrock model |
| `gemini` | Google Gemini |
| `vertex_ai` | Google Vertex AI |
| `azure` | Azure OpenAI |
| `litellm_structured_output` | Any LiteLLM-supported model |

### 4. Metrics (`simpleval/evaluation/metrics/`)

Metrics define what aspects to evaluate. Each metric:

- Extends `BaseMetric` abstract class
- Defines a prompt template for the judge
- Uses parsers (XML or structured output) to extract scores

Available metrics include: correctness, relevance, completeness, faithfulness, coherence, readability, helpfulness, etc.

### 5. Schemas (`simpleval/evaluation/schemas/`)

Pydantic models defining data structures:

- `EvalCase` - Individual evaluation case
- `EvalTask` - Evaluation task definition
- `EvalResult` - Evaluation result
- `EvalTaskConfig` - Configuration for evaluation

### 6. Reporting (`simpleval/commands/reporting/`)

Rich reporting capabilities:

- **Console reports** - Pretty terminal output using `tabulate`
- **HTML reports** - Interactive React-based reports (`reports-frontend/`)
- **Compare** - Side-by-side comparison of evaluation runs
- **Summarize** - Aggregate testcase results

### 7. React Frontend (`reports-frontend/`)

A React + Vite application for generating interactive HTML reports:

- Uses Tailwind CSS and Material-UI
- Chart.js for visualizations
- Separate report types: eval, compare, summary

---

## Directory Structure

```
simple-llm-eval/
├── simpleval/              # Main Python package
│   ├── main.py             # CLI entry point
│   ├── cli_args.py         # CLI argument definitions
│   ├── consts.py           # Constants
│   ├── logger.py           # Logging configuration
│   ├── exceptions.py       # Custom exceptions
│   ├── validations.py      # Validation utilities
│   ├── evaluation/         # Core evaluation system
│   │   ├── eval_runner.py
│   │   ├── llm_task_runner.py
│   │   ├── judges/         # Judge implementations
│   │   ├── metrics/        # Metric implementations
│   │   └── schemas/        # Pydantic schemas
│   ├── commands/           # CLI commands
│   │   ├── run_command.py
│   │   ├── init_command/
│   │   ├── reporting/      # Report generation
│   │   └── ...
│   ├── utilities/          # Utility modules
│   ├── parallel_runner/    # Parallel execution
│   ├── global_config/      # Global configuration
│   ├── testcases/          # Testcase schemas
│   └── eval_sets/          # Example evaluation sets
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── resources/          # Test resources
├── docs/                   # MkDocs documentation
├── reports-frontend/       # React HTML report frontend
├── ci/                     # CI/CD scripts
├── tools/                  # Utility scripts
├── .github/                # GitHub workflows
├── pyproject.toml          # Project configuration
├── mkdocs.yml              # Documentation config
├── README.md               # Project README
├── CHANGELOG.md            # Version history
└── CONTRIBUTING.md         # Contribution guidelines
```

---

## Data Flow

```
1. User creates an eval_set (testcases + config)
                    │
                    ▼
2. `simpleval run` loads the eval_set
                    │
                    ▼
3. For each testcase:
   - LLM Task Runner gets the response from the model under test
   - Judge evaluates the response using the configured metrics
   - Results are scored and stored
                    │
                    ▼
4. Results saved as JSON/JSONL
                    │
                    ▼
5. Reports generated (console/HTML)
```

---

## Configuration

- **`pyproject.toml`** - Project metadata, dependencies, build config
- **Eval sets** (`simpleval/eval_sets/`) - Example evaluation configurations
- **Global config** (`simpleval/global_config/`) - Retry policies, etc.

---

## Key Dependencies

| Package | Purpose |
|---------|---------|
| `litellm` | Unified LLM API interface |
| `click` | CLI framework |
| `pydantic` | Data validation/schemas |
| `tenacity` | Retry logic |
| `boto3` | AWS Bedrock support |
| `google-genai` | Google AI support |
| `tqdm` | Progress bars |
| `tabulate` | Table formatting |
| `inquirerpy` | Interactive prompts |
| `colorama` | Colored terminal output |

---

## Summary

**simpleval** provides a complete, extensible framework for LLM evaluation where:

1. You define **testcases** (inputs and expected outputs)
2. A **judge** (another LLM) evaluates responses against **metrics**
3. Results are reported via console or interactive HTML reports

The modular design allows easy addition of new LLM providers (judges) and evaluation criteria (metrics).

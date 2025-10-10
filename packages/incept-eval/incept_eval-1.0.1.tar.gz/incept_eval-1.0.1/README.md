# Incept Eval

CLI tool for evaluating educational questions with configurable AI-powered modules.

[![PyPI version](https://badge.fury.io/py/incept-eval.svg)](https://badge.fury.io/py/incept-eval)
[![Python Version](https://img.shields.io/pypi/pyversions/incept-eval.svg)](https://pypi.org/project/incept-eval/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

🎯 **Multiple Evaluation Modules**
- **V3 Evaluation** - Scaffolding and DI compliance
- **Answer Verification** - GPT-4 powered correctness checking
- **EduBench Tasks** - Educational quality benchmarks (QA, EC, IP, AG)

⚙️ **Configurable**
- Enable/disable modules per evaluation
- Custom module combinations
- Save configurations for reuse

🚀 **Easy to Use**
- Simple CLI interface
- JSON input/output
- Batch processing support

## Installation

```bash
pip install incept-eval
```

## Quick Start

### 1. Get API Key

Get your API key at [https://incept.ai/api-keys](https://incept.ai/api-keys)

### 2. Configure

```bash
incept-eval configure YOUR_API_KEY
```

### 3. Evaluate

```bash
# Generate example
incept-eval example > questions.json

# Evaluate
incept-eval evaluate questions.json --pretty
```

## Usage

### Evaluate Questions

```bash
# Full evaluation (all modules)
incept-eval evaluate questions.json --output results.json --pretty

# Only V3 evaluation
incept-eval evaluate questions.json --no-answer-verify --edubench

# Only answer verification
incept-eval evaluate questions.json --no-v3 --edubench

# Custom modules
incept-eval evaluate questions.json --edubench QA --edubench EC
```

### Quick Single Question

```bash
incept-eval quick-eval "What is 2+2?" "4" --grade 2 --pretty
```

## Input Format

```json
{
  "request": {
    "grade": 3,
    "subject": "mathematics",
    "instructions": "Generate multiplication problems",
    "language": "english",
    "count": 2
  },
  "questions": [
    {
      "type": "mcq",
      "question": "What is 3 × 7?",
      "answer": "21",
      "difficulty": "medium",
      "explanation": "Multiply 3 by 7",
      "options": {"A": "18", "B": "21", "C": "24", "D": "28"},
      "answer_choice": "B"
    }
  ]
}
```

## Authentication

Three ways to provide your API key:

**1. Config file (recommended)**
```bash
incept-eval configure YOUR_API_KEY
```

**2. Environment variable**
```bash
export INCEPT_API_KEY=YOUR_API_KEY
```

**3. Command line**
```bash
incept-eval evaluate questions.json --api-key YOUR_API_KEY
```

## Commands

| Command | Description |
|---------|-------------|
| `configure` | Save API key to config |
| `evaluate` | Evaluate questions from file |
| `quick-eval` | Quick single question evaluation |
| `example` | Generate example input |
| `modules` | Show available modules |

## Evaluation Modules

### V3 Evaluation
- Scaffolding quality assessment
- Direct Instruction (DI) compliance
- Pedagogical structure validation

### Answer Verification
- GPT-4 powered correctness checking
- Mathematical accuracy validation
- Confidence scoring

### EduBench Tasks
- **QA**: Question Answering evaluation
- **EC**: Error Correction analysis
- **IP**: Instructional Planning assessment
- **AG**: Answer Generation

## Examples

### Quality Assurance Pipeline

```bash
incept-eval evaluate questions.json --output qa_results.json --verbose
```

### Fast Validation

```bash
incept-eval evaluate questions.json --no-v3 --edubench
```

### Batch Processing

```bash
for file in questions/*.json; do
  incept-eval evaluate "$file" --output "results/$(basename $file)"
done
```

## Requirements

- Python >= 3.11
- Incept API key

## Support

- **Issues**: [GitHub Issues](https://github.com/incept-ai/incept-eval/issues)
- **Documentation**: [CLI Usage Guide](https://github.com/incept-ai/incept-eval/blob/main/CLI_USAGE.md)
- **API Keys**: [https://incept.ai/api-keys](https://incept.ai/api-keys)

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by the Incept Team**

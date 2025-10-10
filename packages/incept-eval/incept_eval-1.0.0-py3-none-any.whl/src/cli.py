"""
Incept Unified Evaluator CLI

Command-line interface for running educational question evaluations with configurable modules.
"""

import click
import json
import sys
import os
from pathlib import Path
from typing import Optional, List
from pydantic import ValidationError
from dotenv import load_dotenv

from src.dto.question_generation import (
    GenerateQuestionsRequest,
    GeneratedQuestion,
    EvaluationModules,
    UnifiedEvaluationRequest
)
from src.evaluator.unified_evaluator import evaluate_unified_with_response

# Load environment variables
load_dotenv()


def verify_api_key(api_key: Optional[str] = None) -> str:
    """
    Verify API key from parameter, environment, or config file.

    Priority:
    1. --api-key parameter
    2. INCEPT_API_KEY environment variable
    3. ~/.incept/config (JSON file with api_key field)

    Returns verified API key or exits with error.
    """
    # Check parameter
    if api_key:
        return api_key

    # Check environment variable
    env_key = os.getenv('INCEPT_API_KEY')
    if env_key:
        return env_key

    # Check config file
    config_file = Path.home() / '.incept' / 'config'
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                if 'api_key' in config:
                    return config['api_key']
        except Exception:
            pass

    # No API key found
    click.echo("❌ Error: API key required", err=True)
    click.echo("\nProvide your API key using one of these methods:", err=True)
    click.echo("  1. Command line: --api-key YOUR_KEY", err=True)
    click.echo("  2. Environment: export INCEPT_API_KEY=YOUR_KEY", err=True)
    click.echo("  3. Config file: incept-eval configure YOUR_KEY", err=True)
    click.echo("\n💡 Get your API key at: https://incept.ai/api-keys", err=True)
    sys.exit(1)


@click.group()
@click.version_option(version='1.0.0', prog_name='incept-eval')
def cli():
    """
    🎯 Incept Unified Evaluator CLI

    Evaluate educational questions with configurable evaluation modules:
    - V3 Scaffolding/DI compliance
    - GPT-4 Answer verification
    - EduBench educational quality tasks
    """
    pass


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output JSON file (default: stdout)')
@click.option('--api-key', '-k', envvar='INCEPT_API_KEY', help='Incept API key (or set INCEPT_API_KEY env var)')
@click.option('--v3/--no-v3', default=True, help='Enable V3 scaffolding evaluation (default: enabled)')
@click.option('--answer-verify/--no-answer-verify', default=True, help='Enable answer verification (default: enabled)')
@click.option('--edubench', '-e', multiple=True, type=click.Choice(['QA', 'EC', 'IP', 'AG']),
              help='EduBench tasks to run (can specify multiple times, default: QA,EC,IP)')
@click.option('--pretty', is_flag=True, help='Pretty-print JSON output')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output with progress')
def evaluate(
    input_file: str,
    output: Optional[str],
    api_key: Optional[str],
    v3: bool,
    answer_verify: bool,
    edubench: tuple,
    pretty: bool,
    verbose: bool
):
    """
    Evaluate questions from a JSON file.

    INPUT_FILE should contain:
    {
      "request": {"grade": 3, "count": 2, "subject": "mathematics", ...},
      "questions": [{"type": "mcq", "question": "...", "answer": "...", ...}]
    }

    Example:

        incept-eval evaluate input.json --output results.json --pretty

        incept-eval evaluate input.json --no-v3 --edubench QA

        incept-eval evaluate input.json --no-answer-verify --edubench QA --edubench EC
    """
    try:
        # Verify API key
        verified_key = verify_api_key(api_key)
        if verbose:
            click.echo(f"🔑 API key verified")

        # Load input file
        if verbose:
            click.echo(f"📂 Loading input from: {input_file}")

        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Validate required fields
        if 'request' not in data or 'questions' not in data:
            click.echo("❌ Error: Input file must contain 'request' and 'questions' fields", err=True)
            sys.exit(1)

        # Parse request and questions
        try:
            request = GenerateQuestionsRequest(**data['request'])
            questions = [GeneratedQuestion(**q) for q in data['questions']]
        except ValidationError as e:
            click.echo(f"❌ Validation Error: {e}", err=True)
            sys.exit(1)

        # Build module configuration
        edubench_tasks = list(edubench) if edubench else ["QA", "EC", "IP"]
        if not edubench and not v3 and not answer_verify:
            # If no modules specified, skip edubench
            edubench_tasks = []

        modules = EvaluationModules(
            v3_evaluation=v3,
            answer_verification=answer_verify,
            edubench_tasks=edubench_tasks if edubench_tasks else None
        )

        if verbose:
            click.echo(f"⚙️  Module Configuration:")
            click.echo(f"   - V3 Evaluation: {'✓' if v3 else '✗'}")
            click.echo(f"   - Answer Verification: {'✓' if answer_verify else '✗'}")
            click.echo(f"   - EduBench Tasks: {edubench_tasks if edubench_tasks else 'None'}")
            click.echo(f"🔍 Evaluating {len(questions)} questions...")

        # Run evaluation
        result = evaluate_unified_with_response(
            request=request,
            questions=questions,
            modules=modules
        )

        # Format output
        json_output = json.dumps(result, indent=2 if pretty else None, ensure_ascii=False)

        # Write output
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(json_output)
            if verbose:
                click.echo(f"✅ Results written to: {output}")
        else:
            click.echo(json_output)

        # Summary
        if verbose:
            summary = result.get('summary', {})
            click.echo(f"\n📊 Summary:")
            click.echo(f"   - Questions Evaluated: {summary.get('questions_evaluated', 0)}")
            click.echo(f"   - Time: {summary.get('evaluation_time_seconds', 0):.2f}s")
            click.echo(f"   - Recommendation: {summary.get('recommendation', 'N/A')}")

            overall = result.get('overall_scores', {})
            if 'v3_average' in overall:
                click.echo(f"   - V3 Average: {overall['v3_average']:.2%}")
            if 'answer_correctness_rate' in overall:
                click.echo(f"   - Answer Correctness: {overall['answer_correctness_rate']:.2%}")

    except FileNotFoundError:
        click.echo(f"❌ Error: File not found: {input_file}", err=True)
        sys.exit(1)
    except json.JSONDecodeError as e:
        click.echo(f"❌ Error: Invalid JSON in input file: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('question_text')
@click.argument('answer')
@click.option('--api-key', '-k', envvar='INCEPT_API_KEY', help='Incept API key (or set INCEPT_API_KEY env var)')
@click.option('--explanation', '-e', help='Answer explanation')
@click.option('--grade', '-g', type=int, default=5, help='Grade level (default: 5)')
@click.option('--subject', '-s', default='mathematics', help='Subject (default: mathematics)')
@click.option('--pretty', is_flag=True, help='Pretty-print JSON output')
def quick_eval(question_text: str, answer: str, api_key: Optional[str], explanation: Optional[str], grade: int, subject: str, pretty: bool):
    """
    Quick evaluation of a single question.

    Example:

        incept-eval quick-eval "What is 2+2?" "4" --grade 2 --pretty

        incept-eval quick-eval "Solve: 2x+5=13" "4" -e "Subtract 5, divide by 2" -g 8
    """
    try:
        # Verify API key
        verified_key = verify_api_key(api_key)

        # Build minimal request
        request = GenerateQuestionsRequest(
            grade=grade,
            count=1,
            subject=subject,
            instructions=f"Evaluate this {subject} question"
        )

        # Build question
        question = GeneratedQuestion(
            type="mcq",
            question=question_text,
            answer=answer,
            difficulty="medium",
            explanation=explanation or "No explanation provided"
        )

        # Use default modules (all enabled)
        modules = EvaluationModules()

        click.echo(f"🔍 Evaluating question: {question_text[:50]}...")

        # Run evaluation
        result = evaluate_unified_with_response(
            request=request,
            questions=[question],
            modules=modules
        )

        # Output
        json_output = json.dumps(result, indent=2 if pretty else None, ensure_ascii=False)
        click.echo(json_output)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def example():
    """
    Generate example input JSON file.
    """
    example_data = {
        "request": {
            "grade": 3,
            "count": 2,
            "subject": "mathematics",
            "instructions": "Generate multiplication word problems",
            "language": "arabic"
        },
        "questions": [
            {
                "type": "mcq",
                "question": "إذا كان لديك 4 علب من القلم وكل علبة تحتوي على 7 أقلام، كم عدد الأقلام لديك إجمالاً؟",
                "answer": "28",
                "difficulty": "medium",
                "explanation": "استخدام ضرب لحساب مجموع الأقلام في جميع العلب.",
                "options": {
                    "A": "21",
                    "B": "32",
                    "C": "35",
                    "D": "28"
                },
                "answer_choice": "D"
            },
            {
                "type": "mcq",
                "question": "ما هو حاصل ضرب 6 × 8؟",
                "answer": "48",
                "difficulty": "easy",
                "explanation": "6 × 8 = 48",
                "options": {
                    "A": "42",
                    "B": "48",
                    "C": "54",
                    "D": "56"
                },
                "answer_choice": "B"
            }
        ]
    }

    click.echo(json.dumps(example_data, indent=2, ensure_ascii=False))
    click.echo("\n💡 Save this to a file and use: incept-eval evaluate <file>", err=True)


@cli.command()
@click.argument('api_key')
def configure(api_key: str):
    """
    Save API key to configuration file.

    Saves the API key to ~/.incept/config for future use.

    Example:

        incept-eval configure YOUR_API_KEY_HERE
    """
    try:
        # Create config directory
        config_dir = Path.home() / '.incept'
        config_dir.mkdir(exist_ok=True)

        # Save API key
        config_file = config_dir / 'config'
        config = {'api_key': api_key}

        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        # Set file permissions to user-only
        config_file.chmod(0o600)

        click.echo(f"✅ API key saved to {config_file}")
        click.echo("You can now use incept-eval without --api-key flag")

    except Exception as e:
        click.echo(f"❌ Error saving configuration: {e}", err=True)
        sys.exit(1)


@cli.command()
def modules():
    """
    Show available evaluation modules and their descriptions.
    """
    click.echo("📦 Available Evaluation Modules:\n")

    click.echo("1️⃣  V3 Evaluation (--v3 / --no-v3)")
    click.echo("   └─ Scaffolding and DI compliance evaluation")
    click.echo("   └─ Checks pedagogical structure and instructional design\n")

    click.echo("2️⃣  Answer Verification (--answer-verify / --no-answer-verify)")
    click.echo("   └─ GPT-4 powered answer correctness checking")
    click.echo("   └─ Validates mathematical accuracy and reasoning\n")

    click.echo("3️⃣  EduBench Tasks (--edubench <task>)")
    click.echo("   └─ QA  : Question Answering evaluation")
    click.echo("   └─ EC  : Error Correction analysis")
    click.echo("   └─ IP  : Instructional Planning assessment")
    click.echo("   └─ AG  : Answer Generation (optional)\n")

    click.echo("💡 Examples:")
    click.echo("   incept-eval evaluate input.json --v3 --no-answer-verify")
    click.echo("   incept-eval evaluate input.json --edubench QA --edubench EC")
    click.echo("   incept-eval evaluate input.json --no-v3 --edubench IP\n")


if __name__ == '__main__':
    cli()

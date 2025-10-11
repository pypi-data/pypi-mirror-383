"""CLI for Incept Eval"""
import click
import json
import sys
import os
from pathlib import Path
import requests
from .client import InceptClient

def get_api_key(api_key=None):
    if api_key:
        return api_key
    if os.getenv('INCEPT_API_KEY'):
        return os.getenv('INCEPT_API_KEY')
    config_file = Path.home() / '.incept' / 'config'
    if config_file.exists():
        try:
            with open(config_file) as f:
                return json.load(f).get('api_key')
        except:
            pass
    click.echo("❌ Error: API key required", err=True)
    click.echo("\nProvide API key:", err=True)
    click.echo("  1. --api-key YOUR_KEY", err=True)
    click.echo("  2. export INCEPT_API_KEY=YOUR_KEY", err=True)
    click.echo("  3. incept-eval configure YOUR_KEY", err=True)
    sys.exit(1)

@click.group()
@click.version_option(version='1.0.2')
def cli():
    """Incept Eval - Evaluate educational questions via Incept API

    \b
    CLI tool for evaluating educational questions with comprehensive
    assessment including V3 scaffolding, answer verification, and
    EduBench task evaluation.

    \b
    Commands:
      evaluate    Evaluate questions from a JSON file
      example     Generate sample input JSON file
      configure   Save API key to config file
      help        Show detailed help and usage examples

    \b
    Quick Start:
      1. Configure your API key:
         $ incept-eval configure YOUR_API_KEY

      2. Generate a sample file:
         $ incept-eval example -o test.json

      3. Evaluate questions:
         $ incept-eval evaluate test.json --verbose

    \b
    Examples:
      # Basic evaluation (pretty mode by default)
      $ incept-eval evaluate questions.json

      # Save full results to file
      $ incept-eval evaluate questions.json --no-pretty -o results.json

      # Append multiple evaluations to one file
      $ incept-eval evaluate test1.json -a all_results.json
      $ incept-eval evaluate test2.json -a all_results.json

      # Use local API server
      $ incept-eval evaluate test.json --api-url http://localhost:8000

    \b
    For detailed help, run: incept-eval help
    """
    pass

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Save results to file (overwrites)')
@click.option('--append', '-a', type=click.Path(), help='Append results to file (creates if not exists)')
@click.option('--api-key', '-k', envvar='INCEPT_API_KEY', help='API key for authentication')
@click.option('--api-url', default='https://uae-poc.inceptapi.com', help='API endpoint URL')
@click.option('--pretty', is_flag=True, default=True, help='Show only scores (default: enabled)')
@click.option('--verbose', '-v', is_flag=True, help='Show progress messages')
def evaluate(input_file, output, append, api_key, api_url, pretty, verbose):
    """Evaluate questions from JSON file via Incept API

    Sends questions to the Incept API for comprehensive evaluation including:
    - V3 scaffolding and DI compliance scoring
    - Answer correctness verification
    - EduBench task evaluation (QA, EC, IP)

    By default, shows only scores in pretty format. Use --no-pretty for full results.
    """
    try:
        api_key = get_api_key(api_key)
        if verbose:
            click.echo(f"📂 Loading: {input_file}")

        with open(input_file) as f:
            data = json.load(f)

        client = InceptClient(api_key, api_url)
        result = client.evaluate_dict(data)

        # Extract only scores if pretty flag is set and no file output
        if pretty and not output and not append:
            scores_only = {
                "overall_scores": result.get("overall_scores", {}),
                "v3_scores": result.get("v3_scores", []),
                "answer_verification": result.get("answer_verification", [])
            }
            json_output = json.dumps(scores_only, indent=2, ensure_ascii=False)
        else:
            json_output = json.dumps(result, indent=2 if pretty else None, ensure_ascii=False)

        # Handle output options
        if output:
            # Overwrite mode
            with open(output, 'w', encoding='utf-8') as f:
                f.write(json_output)
            if verbose:
                click.echo(f"✅ Saved to: {output}")
        elif append:
            # Append mode - load existing evaluations or create new list
            existing_data = []
            if Path(append).exists():
                try:
                    with open(append, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                        if not isinstance(existing_data, list):
                            # If file exists but isn't a list, wrap it
                            existing_data = [existing_data]
                except json.JSONDecodeError:
                    if verbose:
                        click.echo(f"⚠️  File exists but is invalid JSON, creating new file")
                    existing_data = []

            # Append new result
            existing_data.append(result)

            # Write back to file
            with open(append, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)

            if verbose:
                click.echo(f"✅ Appended to: {append} (total: {len(existing_data)} evaluations)")
        else:
            # Print to stdout
            click.echo(json_output)

    except requests.HTTPError as e:
        click.echo(f"❌ API Error: {e.response.status_code}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('api_key')
def configure(api_key):
    """Save API key to config file"""
    try:
        config_dir = Path.home() / '.incept'
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / 'config'

        with open(config_file, 'w') as f:
            json.dump({'api_key': api_key}, f)

        config_file.chmod(0o600)
        click.echo(f"✅ API key saved to {config_file}")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@cli.command()
def help():
    """Show detailed help and usage examples"""
    help_text = """
╔═══════════════════════════════════════════════════════════════════╗
║                    INCEPT-EVAL CLI HELP                           ║
╚═══════════════════════════════════════════════════════════════════╝

OVERVIEW:
  Incept Eval is a CLI tool for evaluating educational questions using
  the Incept API. It supports comprehensive evaluation including:
  - V3 scaffolding/DI compliance scoring
  - Answer correctness verification
  - EduBench task evaluation (QA, EC, IP, AG)

INSTALLATION:
  pip install incept-eval

COMMANDS:

  1. configure - Save your API key
     Usage: incept-eval configure YOUR_API_KEY

     This saves your API key to ~/.incept/config for future use.

  2. example - Generate sample input file
     Usage: incept-eval example [OPTIONS]

     Options:
       -o, --output PATH    Save to file (default: print to stdout)

     Examples:
       incept-eval example > test.json
       incept-eval example -o sample.json

  3. evaluate - Evaluate questions from JSON file
     Usage: incept-eval evaluate INPUT_FILE [OPTIONS]

     Options:
       -o, --output PATH      Save results to file (overwrites)
       -a, --append PATH      Append results to file (creates if not exists)
       -k, --api-key KEY      API key (or use INCEPT_API_KEY env var)
       --api-url URL          API endpoint (default: https://uae-poc.inceptapi.com)
       --pretty               Show only scores (default: enabled)
       --no-pretty            Show full results including EduBench details
       -v, --verbose          Show progress messages

     Examples:
       # Basic evaluation (pretty mode by default)
       incept-eval evaluate test.json

       # Full results
       incept-eval evaluate test.json --no-pretty

       # Save to file (overwrite)
       incept-eval evaluate test.json -o results.json

       # Append to file (creates if not exists)
       incept-eval evaluate test.json -a evaluations.json --verbose

       # Local API testing
       incept-eval evaluate test.json --api-url http://localhost:8000

API KEY CONFIGURATION (3 methods):

  1. Config file (recommended):
     incept-eval configure YOUR_API_KEY

  2. Environment variable:
     export INCEPT_API_KEY=your_api_key
     incept-eval evaluate test.json

  3. Command line flag:
     incept-eval evaluate test.json --api-key your_api_key

INPUT FILE FORMAT:

  The input JSON file must contain:
  - request: Question generation request metadata
  - questions: Array of 1-5 questions to evaluate

  Use 'incept-eval example' to see a complete example.

OUTPUT FORMAT:

  Pretty mode (default):
  - overall_scores: Aggregate metrics across all evaluators
  - v3_scores: Per-question scaffolding/DI compliance scores
  - answer_verification: Answer correctness checks

  Full mode (--no-pretty):
  - All of the above, plus:
  - edubench_results: Full task-specific evaluation results
  - summary: Evaluation metadata and timing

QUICK START:

  # 1. Configure API key
  incept-eval configure YOUR_API_KEY

  # 2. Generate sample file
  incept-eval example -o test.json

  # 3. Evaluate questions
  incept-eval evaluate test.json --pretty --verbose

  # 4. Save results (overwrite)
  incept-eval evaluate test.json -o results.json

  # 5. Append multiple evaluations to one file
  incept-eval evaluate test1.json -a all_results.json
  incept-eval evaluate test2.json -a all_results.json
  incept-eval evaluate test3.json -a all_results.json

LOCAL TESTING:

  To test against a local API server:
  incept-eval evaluate test.json --api-url http://localhost:8000

For more information, visit: https://github.com/incept-ai/incept-eval
"""
    click.echo(help_text)

@cli.command()
@click.option('--output', '-o', type=click.Path(), help='Save to file instead of printing')
def example(output):
    """Generate sample test_questions.json file

    Creates a complete example with Arabic math question including
    detailed explanations, voiceover scripts, and DI formats.
    """
    example_data = {
        "request": {
            "grade": 3,
            "count": 2,
            "subject": "mathematics",
            "instructions": "Generate multiplication word problems that involve equal groups.",
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
                "answer_choice": "D",
                "detailed_explanation": {
                    "steps": [
                        {
                            "title": "الخطوة 1: تحليل المشكلة",
                            "content": "لدينا 4 علب من الأقلام وكل علبة تحتوي على 7 أقلام. فكر في عدد العلب وعدد الأقلام في كل واحدة. ما الذي نحتاج للعثور عليه؟ عدد الأقلام إجمالاً. تذكّر كيف يمكن للgrupper المتساوية أن تساعد في إيجاد الإجابات. هل يمكننا استخدام ضرب في هذه الحالة؟",
                            "image": None,
                            "image_alt_text": None
                        },
                        {
                            "title": "الخطوة 2: تطوير الاستراتيجية",
                            "content": "لنستخدم فكر المجموعات المتساوية. إذا كان لدينا 4 مجموعات وكل مجموعة بها 7 أشياء، فكيف يمكننا أن نحسب المجموع الكلي؟ تذكر كيف تعلمنا ضرب الأعداد. كيف يمكننا أن نطبق هذه الفكرة هنا؟",
                            "image": None,
                            "image_alt_text": None
                        },
                        {
                            "title": "الخطوة 3: التقديم والتحقق",
                            "content": "بعد حسابك، كيف يمكنك التأكد من صحة إجابتك؟ فكر في معنى الضرب وكيف يمكن أن يساعدك في التحقق. هل الإجابة منطقية في سياق السؤال؟",
                            "image": None,
                            "image_alt_text": None
                        }
                    ],
                    "personalized_academic_insights": [
                        {
                            "answer": "11",
                            "insight": "قد يكون الخطأ في إضافة العددين فقط. تذكر، لدينا 4 مجموعات من 7، وليس مجموع 4 و7."
                        },
                        {
                            "answer": "21",
                            "insight": "يبدو أنك ضرب 3 في 7. تأكد من ضرب العدد الصحيح للمجموعات، وهو 4، في عدد الأقلام في كل واحدة."
                        },
                        {
                            "answer": "35",
                            "insight": "قد تكون قد أضفت بدلاً من ضرب. عندما نقول 4 علب من 7 أقلام، فهذا يعني ضرب 4 في 7."
                        }
                    ]
                },
                "voiceover_script": {
                    "question_script": "إذا كان لديك 4 علب من القلم وكل علبة تحتوي على 7 أقلام، كم عدد الأقلام لديك إجمالاً؟",
                    "answer_choice_scripts": [],
                    "explanation_step_scripts": []
                },
                "skill": None,
                "image_url": None,
                "di_formats_used": [
                    {
                        "title": "SINGLE DIGIT MULTIPLICATION",
                        "skill_name": "Multiplication",
                        "format_number": "9.1",
                        "score": 0.7,
                        "steps": [
                            "(Display the following boxes on the board.)\n5 5 5",
                            "We're going to learn a fast way to work problems that talk about the same number time and time again. (Highlight each column and ask the following question.) How many in this group?",
                            "When we talk about the same number time and time again, we make a times problem. What number are we talking about time and time again? So we write 5. (Display 5.) How many groups of 5 do we have? To correct: Count the groups of 5. (Highlight each group as students count.) So I write times 3. (Display × 3.)",
                            "Read the problem. We can figure out 5 × 3 a fast way. We count by 5 three times: (Highlight each group of 5 as you count.) 5,10,15. There are 15 in all.",
                            "Let's count by ones and make sure 15 is right. (Highlight each individual member as students count.) 1, 2, 3, 4 . . .15 Are there 15? So we can count the fast way when we talk about the same number time and time again. (Repeat steps 1-4 with the following boxes.)\n□ □ □ □\n□ □ □ □",
                            "(Display these partial problems on the board.)\n5 ×\n10 ×\n2 X\n9 ×",
                            "(Highlight ×.) This sign tells you to count by. What does it tell you to do?",
                            "(Highlight 5 ×.) So this tells you to count by 5. What does this tell you to do?",
                            "(Highlight 10 ×.) What does this tell you to do?",
                            "(Highlight 2 ×.) What does this tell you to do?",
                            "(Highlight 9 ×) What does this tell you to do?",
                            "(Highlight 5 ×.) What does this tell you to do? (Display 3 after 5 X: 5 x 3.) Now this problem tells you to count by 5 three times. What does this problem tell you to do?",
                            "(Highlight 10 ×.) What does this problem tell you to do? (Display 4 after 10: 10 x 4.) What does this problem tell you to do now?",
                            "(Highlight 2 ×.) What does this problem tell you to do? (Display 5 after 2 X: 2 x 5.) What does this problem tell you to do now?",
                            "(Highlight 9 ×.) What does this problem tell you to do? (Display 4 after 9 X: 9 × 4.) What does the problem tell you to do now?",
                            "Let's start over. (Highlight 5 × 3.) What does this problem tell you to do? (Repeat step 11 with each problem. Give individual turns to several students.)",
                            "(Display this problem on the board.) 2 × 5 = □",
                            "What does this problem tell us to do? (Highlight problem as students read.) How many times are we going to count? So I'll put up five fingers. Watch me count by 2 five times: (Count and touch fingers.) 2, 4, 6, 8, 10.",
                            "Now it's your turn to count by 2 five times. How many times are you going to count? Hold up five fingers. You're counting by 2 five times. What number are you going to count by? Touch a finger every time you count. Counting by 2. Get ready, count. (Clap at intervals of 2 seconds.) What number did you end with? So I'll write a 10 in the box. (Display 10.)",
                            "(Display the problem below on the board.) 2 × 3 = □",
                            "What does this problem tell us to do? How many times are you going to count? Hold up your fingers. (Monitor students' responses.) What number are you going to count by? Get ready to count. (Clap at intervals of 2 seconds.) How many did you end with? So I'll write 6 in the box. (Display 6.) When we count by 2 three times, what do we end with?",
                            "(Repeat steps 4 and 5 with 5 × 4 = □, 10 × 3 = □, 2 X 4 = □, and 9 × 3 = □). (Give individual turns to several students.)",
                            "(Give students a worksheet with problems like the following.)\na. 5 × 3 = □\nb. 10 × 4 = □\nc. 2 × 6 = □",
                            "(Highlight problem a.) What does the problem tell you to do? How many times are you going to count? Hold up your fingers. (Monitor responses.) What number are you counting by?",
                            "Get ready. Count. (Clap at intervals of about 1 second.) When you count by 5 three times, what do you end with? Write 15 in the box. (Check student work.) (Repeat steps 2 and 3 with remaining problems.)",
                            "(Give students a worksheet with a variety of multiplication and addition problems like the following.)\na. 5 × 4 = □\nb. 5 + 4 = □\nc. 10 × 3 = □\nd. 10 × 5 = □\ne. 10 + 5 = □",
                            "Highlight problem a. Put your finger under the sign. What does the problem tell you to do, plus or count by? Say the problem. Work it and write how many you end with in the box. (Monitor student responses.) (Repeat step 2 with remaining problems.)"
                        ],
                        "step_numbers_used": [7, 4, 18, 19, 5, 26],
                        "steps_used": [
                            "(Highlight ×.) This sign tells you to count by. What does it tell you to do?",
                            "Read the problem. We can figure out 5 × 3 a fast way. We count by 5 three times: (Highlight each group of 5 as you count.) 5,10,15. There are 15 in all.",
                            "What does this problem tell us to do? (Highlight problem as students read.) How many times are we going to count? So I'll put up five fingers. Watch me count by 2 five times: (Count and touch fingers.) 2, 4, 6, 8, 10.",
                            "Now it's your turn to count by 2 five times. How many times are you going to count? Hold up five fingers. You're counting by 2 five times. What number are you going to count by? Touch a finger every time you count. Counting by 2. Get ready, count. (Clap at intervals of 2 seconds.) What number did you end with? So I'll write a 10 in the box. (Display 10.)",
                            "Let's count by ones and make sure 15 is right. (Highlight each individual member as students count.) 1, 2, 3, 4 . . .15 Are there 15? So we can count the fast way when we talk about the same number time and time again. (Repeat steps 1-4 with the following boxes.)",
                            "Highlight problem a. Put your finger under the sign. What does the problem tell you to do, plus or count by? Say the problem. Work it and write how many you end with in the box. (Monitor student responses.) (Repeat step 2 with remaining problems.)"
                        ]
                    }
                ]
            }
        ]
    }

    json_output = json.dumps(example_data, indent=2, ensure_ascii=False)

    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(json_output)
        click.echo(f"✅ Sample file saved to: {output}")
    else:
        click.echo(json_output)

if __name__ == '__main__':
    cli()

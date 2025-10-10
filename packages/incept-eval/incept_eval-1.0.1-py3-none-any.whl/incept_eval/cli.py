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
@click.version_option(version='1.0.0')
def cli():
    """Incept Eval - Evaluate educational questions"""
    pass

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path())
@click.option('--api-key', '-k', envvar='INCEPT_API_KEY')
@click.option('--api-url', default='https://uae-poc.inceptapi.com')
@click.option('--pretty', is_flag=True)
@click.option('--verbose', '-v', is_flag=True)
def evaluate(input_file, output, api_key, api_url, pretty, verbose):
    """Evaluate questions from JSON file"""
    try:
        api_key = get_api_key(api_key)
        if verbose:
            click.echo(f"📂 Loading: {input_file}")

        with open(input_file) as f:
            data = json.load(f)

        client = InceptClient(api_key, api_url)
        result = client.evaluate_dict(data)

        json_output = json.dumps(result, indent=2 if pretty else None, ensure_ascii=False)

        if output:
            with open(output, 'w') as f:
                f.write(json_output)
            if verbose:
                click.echo(f"✅ Saved to: {output}")
        else:
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
def example():
    """Generate example input JSON"""
    example_data = {
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
    click.echo(json.dumps(example_data, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    cli()

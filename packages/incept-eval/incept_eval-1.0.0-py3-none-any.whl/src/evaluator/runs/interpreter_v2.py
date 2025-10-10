#!/usr/bin/env python3
"""
Interpreter v2: Pulls evaluation results directly from PostgreSQL database and summarizes by grade, subject, etc.
Uses the same scoring logic as interpreter.py to evaluate EduBench results.
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
import psycopg2
from psycopg2.extras import RealDictCursor

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import scoring functions from interpreter.py
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
from interpreter import (
    parse_results_response_to_json,
    score_from_QA,
    score_from_EC,
    score_from_IP,
)


def get_db_connection():
    """Get PostgreSQL database connection"""
    postgres_uri = os.getenv("POSTGRES_URI")
    if not postgres_uri:
        raise RuntimeError("POSTGRES_URI environment variable not set")
    return psycopg2.connect(postgres_uri)


def fetch_evaluated_questions(conn, limit: Optional[int] = None, grade: Optional[int] = None,
                              subject: Optional[str] = None, language: Optional[str] = None,
                              start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    Fetch all questions that have been evaluated with EduBench

    Args:
        conn: Database connection
        limit: Maximum number of questions to fetch
        grade: Filter by grade level
        subject: Filter by subject area
        language: Filter by language (ar, en)
        start_date: Filter by start date (YYYY-MM-DD)
        end_date: Filter by end date (YYYY-MM-DD)

    Returns:
        List of question dictionaries with evaluation results
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        query = """
            SELECT
                id,
                question_text,
                question_text_arabic,
                correct_answer,
                answer_explanation,
                difficulty_level,
                grade_level,
                normalized_grade,
                subject_area,
                broad_topic,
                subtopic,
                scaffolding,
                language,
                evaluation_edubench,
                evaluation_scaffolding,
                extracted_by_model,
                created_at
            FROM uae_educational_questions_cleaned_duplicate
            WHERE evaluation_edubench IS NOT NULL
        """

        params = []

        if grade is not None:
            query += " AND normalized_grade = %s"
            params.append(grade)

        if subject:
            query += " AND subject_area ILIKE %s"
            params.append(f"%{subject}%")

        if language:
            query += " AND language = %s"
            params.append(language)

        if start_date:
            query += " AND created_at >= %s"
            params.append(start_date)

        if end_date:
            query += " AND created_at < %s::date + interval '1 day'"
            params.append(end_date)

        query += " ORDER BY created_at DESC"

        if limit:
            query += " LIMIT %s"
            params.append(limit)

        cur.execute(query, params)
        return cur.fetchall()


def score_edubench_result(evaluation_json: Dict[str, Any], question_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Score EduBench evaluation JSON using the same logic as interpreter.py

    Args:
        evaluation_json: The evaluation_edubench JSON object
        question_data: Question data including correct answer

    Returns:
        Dictionary with scores for QA, EC, IP tasks
    """
    scores = {
        'qa_score': None,
        'ec_score': None,
        'ip_score': None,
        'has_qa': False,
        'has_ec': False,
        'has_ip': False,
    }

    gold_answer = question_data.get('correct_answer', '')

    # Score QA task
    if 'QA' in evaluation_json:
        scores['has_qa'] = True
        qa_data = evaluation_json['QA']
        if 'response' in qa_data:
            # Construct fake result object to match interpreter.py format
            fake_result = {
                'results': [{'response': qa_data['response']}],
                'input': {'answer': gold_answer}
            }
            try:
                parsed = parse_results_response_to_json(fake_result)
                if parsed and parsed.get("_source") != "unparseable":
                    score = score_from_QA(parsed, gold_answer)
                    scores['qa_score'] = score
            except Exception as e:
                pass

    # Score EC task
    if 'EC' in evaluation_json:
        scores['has_ec'] = True
        ec_data = evaluation_json['EC']
        if 'response' in ec_data:
            fake_result = {
                'results': [{'response': ec_data['response']}],
                'input': {'original_answer': gold_answer}
            }
            try:
                parsed = parse_results_response_to_json(fake_result)
                if parsed and parsed.get("_source") != "unparseable":
                    score = score_from_EC(parsed, gold_answer)
                    scores['ec_score'] = score
            except Exception as e:
                pass

    # Score IP task
    if 'IP' in evaluation_json:
        scores['has_ip'] = True
        ip_data = evaluation_json['IP']
        if 'response' in ip_data:
            fake_result = {
                'results': [{'response': ip_data['response']}],
                'input': {'answer': gold_answer}
            }
            try:
                parsed = parse_results_response_to_json(fake_result)
                if parsed and parsed.get("_source") != "unparseable":
                    score = score_from_IP(parsed, gold_answer)
                    scores['ip_score'] = score
            except Exception as e:
                pass

    return scores


def summarize_by_grade_model_language(questions: List[Dict[str, Any]]) -> Dict[Tuple[int, str, str], Dict[str, Any]]:
    """
    Summarize evaluation results grouped by grade, model, and language
    Similar to batch_interpreter.py output format

    Args:
        questions: List of question dictionaries with evaluation results

    Returns:
        Dictionary with summaries for each (grade, model, language) group
    """
    groups = defaultdict(lambda: {
        'qa_scores': [],
        'ec_scores': [],
        'ip_scores': [],
        'scaffolding_scores': [],
        'unparsed_count': {'QA': 0, 'EC': 0, 'IP': 0},
        'total_questions': 0
    })

    for question in questions:
        # Extract group keys
        grade = question.get('normalized_grade') or question.get('grade_level', 'Unknown')
        model = question.get('extracted_by_model', 'Unknown').upper()
        language = 'Arabic' if question.get('language') == 'ar' else 'English'

        # Only process orchestrator-pipeline questions
        if 'orchestrator' not in model.lower():
            continue

        # Simplify model names
        if 'orchestrator' in model.lower():
            model = 'INCEPT'
        elif 'gpt' in model.lower() or 'openai' in model.lower():
            model = 'GPT'
        elif 'falcon' in model.lower():
            model = 'FALCON'

        group_key = (grade, model, language)
        group = groups[group_key]
        group['total_questions'] += 1

        # Parse and score evaluation results
        eval_json = question.get('evaluation_edubench')
        if eval_json:
            if isinstance(eval_json, str):
                try:
                    eval_json = json.loads(eval_json)
                except:
                    eval_json = None

            if eval_json:
                scores = score_edubench_result(eval_json, question)

                # Collect scores
                if scores['qa_score'] is not None:
                    group['qa_scores'].append(scores['qa_score'])
                elif scores['has_qa']:
                    group['unparsed_count']['QA'] += 1

                if scores['ec_score'] is not None:
                    group['ec_scores'].append(scores['ec_score'])
                elif scores['has_ec']:
                    group['unparsed_count']['EC'] += 1

                if scores['ip_score'] is not None:
                    group['ip_scores'].append(scores['ip_score'])
                elif scores['has_ip']:
                    group['unparsed_count']['IP'] += 1

        # Extract scaffolding evaluation if present (multiply by 10 to get 0-10 scale)
        eval_scaffolding = question.get('evaluation_scaffolding')
        if eval_scaffolding:
            if isinstance(eval_scaffolding, str):
                try:
                    eval_scaffolding = json.loads(eval_scaffolding)
                except:
                    eval_scaffolding = None

            if eval_scaffolding and isinstance(eval_scaffolding, dict):
                overall_score = eval_scaffolding.get('overall')
                if overall_score is not None:
                    # overall_score is already in 0-1 range, multiply by 10
                    group['scaffolding_scores'].append(overall_score * 10)

    # Calculate averages for each group
    for group_key, data in groups.items():
        data['qa_avg'] = sum(data['qa_scores']) / len(data['qa_scores']) if data['qa_scores'] else 0
        data['ec_avg'] = sum(data['ec_scores']) / len(data['ec_scores']) if data['ec_scores'] else 0
        data['ip_avg'] = sum(data['ip_scores']) / len(data['ip_scores']) if data['ip_scores'] else 0
        data['scaffolding_avg'] = sum(data['scaffolding_scores']) / len(data['scaffolding_scores']) if data['scaffolding_scores'] else 0

        # Calculate weighted score (EC weighted higher for curriculum alignment importance)
        valid_tasks = sum([1 for scores in [data['qa_scores'], data['ec_scores'], data['ip_scores']] if len(scores) > 0])
        if valid_tasks > 0:
            # Weight QA and EC higher as answer accuracy and curriculum alignment are critical for educational standards
            weights = {'qa': 0.35, 'ec': 0.45, 'ip': 0.20}
            data['weighted_score'] = (
                data['qa_avg'] * weights['qa'] +
                data['ec_avg'] * weights['ec'] +
                data['ip_avg'] * weights['ip']
            )
        else:
            data['weighted_score'] = 0

        data['total_parsed'] = len(data['qa_scores']) + len(data['ec_scores']) + len(data['ip_scores'])

    return dict(groups)


def fetch_unevaluated_counts(conn):
    """Fetch counts of unevaluated questions by grade and model"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        query = """
            SELECT
                normalized_grade as grade,
                extracted_by_model,
                language,
                COUNT(*) as unevaluated_count
            FROM uae_educational_questions_cleaned_duplicate
            WHERE evaluation_edubench IS NULL
            AND normalized_grade IS NOT NULL
            GROUP BY normalized_grade, extracted_by_model, language
            ORDER BY normalized_grade, extracted_by_model, language
        """
        cur.execute(query)
        return cur.fetchall()


def fetch_all_question_counts(conn):
    """Fetch counts of ALL questions (evaluated + unevaluated) by grade and model"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        query = """
            SELECT
                normalized_grade as grade,
                extracted_by_model,
                COUNT(*) as total_count
            FROM uae_educational_questions_cleaned_duplicate
            WHERE normalized_grade IS NOT NULL
            GROUP BY normalized_grade, extracted_by_model
            ORDER BY normalized_grade, extracted_by_model
        """
        cur.execute(query)
        return cur.fetchall()


def print_summary_table(summaries: Dict[Tuple[int, str, str], Dict[str, Any]], questions: List[Dict[str, Any]]):
    """
    Print a formatted summary table in the style of batch_interpreter.py

    Args:
        summaries: Dictionary with (grade, model, language) tuples as keys
        questions: All questions for unevaluated count
    """
    print("\n" + "="*130)
    print(f"{'Grade':<15} {'Model':<12} {'QA':>12} {'EC':>12} {'IP':>12} {'Weighted':>10} {'Parsed':>10} {'Total':>8}")
    print("="*130)

    # Sort by weighted score (descending)
    sorted_keys = sorted(summaries.keys(), key=lambda x: summaries[x]['weighted_score'], reverse=True)

    total_parsed = 0
    total_items = 0
    all_weighted_scores = []

    for (grade, model, language) in sorted_keys:
        data = summaries[(grade, model, language)]

        # Format QA/EC/IP columns
        qa_str = f"{data['qa_avg']:.2f} ({len(data['qa_scores'])})" if data['qa_scores'] else "-"
        ec_str = f"{data['ec_avg']:.2f} ({len(data['ec_scores'])})" if data['ec_scores'] else "-"
        ip_str = f"{data['ip_avg']:.2f} ({len(data['ip_scores'])})" if data['ip_scores'] else "-"

        grade_str = f"Grade {grade}" if isinstance(grade, int) else str(grade)

        print(f"{grade_str:<15} {model:<12} {qa_str:>12} {ec_str:>12} {ip_str:>12} "
              f"{data['weighted_score']:>10.2f} {data['total_parsed']:>10} {data['total_questions']:>8}")

        total_parsed += data['total_parsed']
        total_items += data['total_questions']
        if data['weighted_score'] > 0:
            all_weighted_scores.append(data['weighted_score'])


def print_detailed_stats(questions: List[Dict[str, Any]]):
    """Print detailed statistics about evaluated questions"""
    print(f"\n{'='*120}")
    print("Detailed Statistics")
    print(f"{'='*120}")

    total = len(questions)
    print(f"Total evaluated questions: {total}")

    # Language breakdown
    languages = defaultdict(int)
    for q in questions:
        languages[q.get('language', 'Unknown')] += 1

    print(f"\nLanguage breakdown:")
    for lang, count in sorted(languages.items()):
        lang_name = "Arabic" if lang == "ar" else "English" if lang == "en" else lang
        print(f"  {lang_name}: {count} ({count/total*100:.1f}%)")

    # Model breakdown
    models = defaultdict(int)
    for q in questions:
        models[q.get('extracted_by_model', 'Unknown')] += 1

    print(f"\nExtracted by model:")
    for model, count in sorted(models.items()):
        print(f"  {model}: {count} ({count/total*100:.1f}%)")

    # Date range
    dates = [q['created_at'] for q in questions if q.get('created_at')]
    if dates:
        earliest = min(dates)
        latest = max(dates)
        print(f"\nDate range:")
        print(f"  Earliest: {earliest}")
        print(f"  Latest: {latest}")

    print(f"{'='*120}\n")


def export_to_json(summaries: Dict[str, Dict[str, Dict[str, Any]]],
                   questions: List[Dict[str, Any]],
                   output_file: str):
    """
    Export summaries and raw data to JSON file

    Args:
        summaries: Dictionary of summaries by dimension
        questions: Raw question data
        output_file: Path to output JSON file
    """
    output = {
        'generated_at': datetime.now().isoformat(),
        'total_questions': len(questions),
        'summaries': summaries,
        'sample_questions': [
            {
                'id': q['id'],
                'grade': q.get('normalized_grade'),
                'subject': q.get('subject_area'),
                'language': q.get('language'),
                'question': (q['question_text_arabic'] if q['language'] == 'ar'
                           else q['question_text'])[:200]
            }
            for q in questions[:10]  # First 10 as samples
        ]
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✓ Exported summary to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Analyze EduBench evaluation results from database")
    parser.add_argument("--limit", type=int, help="Maximum number of questions to analyze")
    parser.add_argument("--grade", type=int, help="Filter by grade level")
    parser.add_argument("--subject", type=str, help="Filter by subject area")
    parser.add_argument("--language", type=str, help="Filter by language (ar, en)")
    parser.add_argument("--start-date", type=str, help="Filter by start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, help="Filter by end date (YYYY-MM-DD)")
    parser.add_argument("--output", type=str, help="Output JSON file path")
    parser.add_argument("--detailed", action="store_true", help="Show detailed statistics")

    args = parser.parse_args()

    try:
        # Connect to database
        conn = get_db_connection()

        # Fetch evaluated questions
        if args.grade or args.subject or args.language or args.start_date or args.end_date:
            print(f"  Filters: grade={args.grade}, subject={args.subject}, language={args.language}, start_date={args.start_date}, end_date={args.end_date}")

        questions = fetch_evaluated_questions(
            conn,
            limit=args.limit,
            grade=args.grade,
            subject=args.subject,
            language=args.language,
            start_date=args.start_date,
            end_date=args.end_date
        )

        print(f"✓ Fetched {len(questions)} evaluated questions")

        if not questions:
            print("No evaluated questions found with the given filters.")
            return

        # Print detailed statistics if requested
        if args.detailed:
            print_detailed_stats(questions)

        # Summarize by grade, model, and language
        summaries = summarize_by_grade_model_language(questions)

        # Print summary table
        print_summary_table(summaries, questions)

        # Build generation recommendations based on ALL questions in DB
        all_question_counts = fetch_all_question_counts(conn)

        # Count total questions by grade and model from database
        grade_model_totals = defaultdict(lambda: defaultdict(int))
        grade_totals = defaultdict(int)

        for row in all_question_counts:
            grade = row['grade']
            model = row['extracted_by_model'] or 'Unknown'

            # Only count orchestrator-pipeline questions
            if 'orchestrator' not in model.lower():
                continue

            # Simplify model name
            if 'orchestrator' in model.lower():
                model_simple = 'INCEPT'
            elif 'gpt' in model.lower() or 'openai' in model.lower():
                model_simple = 'GPT'
            elif 'falcon' in model.lower():
                model_simple = 'FALCON'
            else:
                model_simple = model

            count = row['total_count']
            grade_model_totals[grade][model_simple] += count
            grade_totals[grade] += count

        # Print generation recommendations - how many to reach 300 per model
        if grade_totals:
            MAX_PER_MODEL = 300

            print("\n" + "="*80)
            print("GENERATION RECOMMENDATIONS (Target: 300 per model)")
            print("="*80)
            print(f"{'Grade':<10} {'Model':<12} {'Total':>10} {'Generate':>12}")
            print("-"*80)

            for grade in sorted(grade_totals.keys()):
                # Get all models for this grade
                models = sorted(grade_model_totals[grade].keys())

                for i, model in enumerate(models):
                    model_total = grade_model_totals[grade][model]

                    # Generate: how many more to reach 300
                    generate = max(0, MAX_PER_MODEL - model_total)

                    # Only show grade on first model row
                    grade_str = f"Grade {grade}" if i == 0 else ""
                    print(f"{grade_str:<10} {model:<12} {model_total:>10} {generate:>12}")

                # Separator between grades
                if grade != sorted(grade_totals.keys())[-1]:
                    print("-"*80)

            print("="*80)

        # Export to JSON if requested
        if args.output:
            output_data = {
                'generated_at': datetime.now().isoformat(),
                'total_questions': len(questions),
                'summaries': {
                    f"Grade {grade} - {model} - {lang}": {
                        'qa_avg': data['qa_avg'],
                        'qa_count': len(data['qa_scores']),
                        'ec_avg': data['ec_avg'],
                        'ec_count': len(data['ec_scores']),
                        'ip_avg': data['ip_avg'],
                        'ip_count': len(data['ip_scores']),
                        'scaffolding_avg': data['scaffolding_avg'],
                        'scaffolding_count': len(data['scaffolding_scores']),
                        'weighted_score': data['weighted_score'],
                        'total_parsed': data['total_parsed'],
                        'total_questions': data['total_questions']
                    }
                    for (grade, model, lang), data in summaries.items()
                }
            }
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            print(f"✓ Exported summary to: {args.output}")

        print(f"\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        if 'conn' in locals():
            conn.close()
            print("✓ Database connection closed")


if __name__ == "__main__":
    main()

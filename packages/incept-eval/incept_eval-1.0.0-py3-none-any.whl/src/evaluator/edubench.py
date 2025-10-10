import os
import sys
import argparse
import json
import re
from pathlib import Path
from datetime import datetime
import requests

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Add EduBench code path
edu_bench_path = Path(__file__).parent / "EduBench" / "code" / "evaluation"
sys.path.insert(0, str(edu_bench_path))

from src.evaluator.utils import load_from_postgres, normalize_generated_question_to_edubench_qg
from src.evaluator.EduBench.code.evaluation.evaluation import process_single_task
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from src.evaluator.v2 import call_single_shot_evaluator, EvaluationDimension


def query_hf_model(payload, max_retries=3, timeout=500):
    """Query the HuggingFace model endpoint with retry logic"""
    # Try multiple sources for the token
    hf_token = (
        os.getenv('HF_TOKEN') or
        os.getenv('HUGGINGFACE_TOKEN') or
        os.getenv('HF_API_TOKEN')
    )

    if not hf_token:
        print("Warning: No HuggingFace token found. Checked: HF_TOKEN, HUGGINGFACE_TOKEN, HF_API_TOKEN")
        print("Please set one of these environment variables with your HuggingFace API token.")
        raise ValueError("HuggingFace API token not found in environment variables")

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://ifkx7sxcl1f3j6k6.us-east-1.aws.endpoints.huggingface.cloud",
                headers=headers,
                json=payload,
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout as e:
            if attempt < max_retries - 1:
                print(f"Timeout on attempt {attempt + 1}/{max_retries}, retrying...")
                continue
            else:
                print(f"Failed after {max_retries} attempts due to timeout")
                raise
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"Request error on attempt {attempt + 1}/{max_retries}: {e}, retrying...")
                continue
            else:
                print(f"Failed after {max_retries} attempts")
                raise


def get_normal_answer(prompt, model_name):
    """Call HF model and return a result"""
    print(f"Calling model: {model_name}")
    try:
        output = query_hf_model({
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.7,
                "do_sample": True
            }
        })

        # Handle different response formats
        response_text = ""
        if isinstance(output, list) and len(output) > 0:
            # Standard text generation response
            if 'generated_text' in output[0]:
                response_text = output[0]['generated_text']
            elif 'text' in output[0]:
                response_text = output[0]['text']
            else:
                response_text = str(output[0])
        elif isinstance(output, dict):
            if 'generated_text' in output:
                response_text = output['generated_text']
            elif 'text' in output:
                response_text = output['text']
            elif 'choices' in output and len(output['choices']) > 0:
                response_text = output['choices'][0].get('text', str(output))
            else:
                response_text = str(output)
        else:
            response_text = str(output)

        # Remove prompt echo if present
        if response_text.startswith(prompt):
            response_text = response_text[len(prompt):].strip()

        return response_text

    except requests.exceptions.RequestException as e:
        print(f"Network error calling {model_name}: {e}")
        return f"Network error from {model_name}: {str(e)}"
    except ValueError as e:
        print(f"Configuration error: {e}")
        return f"Configuration error: {str(e)}"
    except Exception as e:
        print(f"Unexpected error calling {model_name}: {e}")
        return f"Error from {model_name}: {str(e)}"


def get_reasoning_answer(prompt, model_name):
    """Call HF reasoning model"""
    print(f"Calling reasoning model: {model_name}")
    try:
        # Add reasoning prompt prefix for better reasoning responses
        reasoning_prompt = f"Think step by step and provide detailed reasoning:\n\n{prompt}"

        output = query_hf_model({
            "inputs": reasoning_prompt,
            "parameters": {
                "max_new_tokens": 1024,
                "temperature": 0.7,
                "do_sample": True
            }
        })

        # Extract response using same logic as normal answer
        response_text = ""
        if isinstance(output, list) and len(output) > 0:
            if 'generated_text' in output[0]:
                response_text = output[0]['generated_text']
            elif 'text' in output[0]:
                response_text = output[0]['text']
            else:
                response_text = str(output[0])
        elif isinstance(output, dict):
            if 'generated_text' in output:
                response_text = output['generated_text']
            elif 'text' in output:
                response_text = output['text']
            else:
                response_text = str(output)
        else:
            response_text = str(output)

        # Split reasoning and answer (simple approach)
        parts = response_text.split('\n\nFinal Answer:')
        if len(parts) >= 2:
            reasoning = parts[0].strip()
            answer = parts[1].strip()
        else:
            # Try another split pattern
            parts = response_text.split('\n\n')
            if len(parts) >= 2:
                reasoning = parts[0].strip()
                answer = '\n\n'.join(parts[1:]).strip()
            else:
                reasoning = f"Reasoning from {model_name}: Step-by-step analysis provided"
                answer = response_text.strip()

        return reasoning, answer

    except requests.exceptions.RequestException as e:
        print(f"Network error calling reasoning model {model_name}: {e}")
        return f"Network error reasoning from {model_name}: {str(e)}", f"Network error answer from {model_name}: {str(e)}"
    except ValueError as e:
        print(f"Configuration error: {e}")
        return f"Configuration error: {str(e)}", f"Configuration error: {str(e)}"
    except Exception as e:
        print(f"Unexpected error calling reasoning model {model_name}: {e}")
        return f"Error reasoning from {model_name}: {str(e)}", f"Error answer from {model_name}: {str(e)}"


def evaluate_question_scaffolding(question, request):
    """Evaluate question quality using v2 evaluator."""
    try:
        # Convert SkillInfo to dict if present to avoid JSON serialization issues
        if hasattr(question, 'skill') and question.skill is not None:
            if hasattr(question.skill, 'model_dump'):
                question.skill = question.skill.model_dump()
            elif hasattr(question.skill, 'dict'):
                question.skill = question.skill.dict()

        result = call_single_shot_evaluator(question, request, total_questions=1)

        return {
            "scaffolding_scores": {
                "correctness": result["scores"].get(EvaluationDimension.CORRECTNESS, 0.0),
                "grade_alignment": result["scores"].get(EvaluationDimension.GRADE_ALIGNMENT, 0.0),
                "difficulty_alignment": result["scores"].get(EvaluationDimension.DIFFICULTY_ALIGNMENT, 0.0),
                "language_quality": result["scores"].get(EvaluationDimension.LANGUAGE_QUALITY, 0.0),
                "pedagogical_value": result["scores"].get(EvaluationDimension.PEDAGOGICAL_VALUE, 0.0),
                "explanation_quality": result["scores"].get(EvaluationDimension.EXPLANATION_QUALITY, 0.0),
                "instruction_adherence": result["scores"].get(EvaluationDimension.INSTRUCTION_ADHERENCE, 0.0),
                "format_compliance": result["scores"].get(EvaluationDimension.FORMAT_COMPLIANCE, 0.0),
                "di_compliance": result["scores"].get(EvaluationDimension.DI_COMPLIANCE, 0.0),
            },
            "scaffolding_overall": result["overall"],
            "scaffolding_recommendation": result["recommendation"],
            "scaffolding_issues": result["issues"],
            "scaffolding_strengths": result["strengths"],
            "scaffolding_improvements": result["suggested_improvements"],
            "di_scores": result.get("di_scores", {})
        }
    except Exception as e:
        print(f"Error evaluating question scaffolding: {e}")
        raise e 


def verify_answer_with_gpt4(question_text, expected_answer, explanation):
    """Use GPT-4 to verify if the expected answer is actually correct."""
    try:
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            return {"is_correct": None, "gpt4_answer": None, "confidence": 0}

        prompt = f"""Given this educational question, determine if the provided answer is correct.

Question: {question_text}

Provided Answer: {expected_answer}
Provided Explanation: {explanation}

Please analyze:
1. Is the provided answer mathematically/logically correct?
2. What is the correct answer if different?
3. Your confidence level (0-10)

Return ONLY a JSON object:
{{"is_correct": true/false, "correct_answer": "your answer", "confidence": 0-10, "reasoning": "brief explanation"}}"""

        headers = {
            "Authorization": f"Bearer {openai_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json={
                "model": "gpt-5",
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30
        )

        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
                return result

        return {"is_correct": None, "gpt4_answer": None, "confidence": 0}

    except Exception as e:
        print(f"Error verifying answer with GPT-4: {e}")
        return {"is_correct": None, "gpt4_answer": None, "confidence": 0}


def process_single_task_with_scaffolding(task_id, task_type, input_data, normal_models, reasoning_models,
                                         output_file, get_normal_answer, get_reasoning_answer,
                                         scaffolding_results, answer_verification_results):
    """Wrapper to add scaffolding evaluation and answer verification to task results with error handling."""
    import threading
    import json
    from datetime import datetime

    write_lock = threading.Lock()

    try:
        # Get the original question ID
        original_id = input_data.get('original_item_id')

        # Build the output with scaffolding data
        from src.evaluator.EduBench.code.evaluation.evaluation import TASK_PROMPT_TEMPLATES

        if task_type == "QA":
            prompt_content = TASK_PROMPT_TEMPLATES["QA"](input_data.get("question", ""))
        elif task_type == "EC":
            prompt_content = TASK_PROMPT_TEMPLATES["EC"](input_data.get("question", ""), input_data.get("original_answer", ""))
        elif task_type == "IP":
            prompt_content = TASK_PROMPT_TEMPLATES["IP"](input_data.get("question", ""))
        else:
            prompt_content = ""

        results = []
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def process_model(model):
            try:
                response = get_normal_answer(prompt_content, model)
                return {'model': model, 'reasoning': None, 'response': response}
            except Exception as e:
                print(f"Model {model} call failed: {e}")
                return {'model': model, 'reasoning': None, 'response': f"Error: {str(e)}", 'error': str(e)}

        with ThreadPoolExecutor(max_workers=5) as model_executor:
            futures = [model_executor.submit(process_model, model) for model in normal_models]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)

        # Construct output
        output = {
            "task_id": task_id,
            "task_type": task_type,
            "input": input_data,
            "results": results,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Add scaffolding evaluation
        if original_id in scaffolding_results:
            output["scaffolding_evaluation"] = scaffolding_results[original_id]

        # Add answer verification
        if original_id in answer_verification_results:
            output["answer_verification"] = answer_verification_results[original_id]

        # Write to file
        with write_lock:
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(output, ensure_ascii=False) + '\n')

        return task_id

    except Exception as e:
        print(f"Error processing task {task_id}: {e}")
        # Write error to file so we don't lose track
        error_output = {
            "task_id": task_id,
            "task_type": task_type,
            "error": str(e),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        try:
            with write_lock:
                with open(output_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(error_output, ensure_ascii=False) + '\n')
        except:
            pass
        return task_id


def extract_score_from_response(response_text, task_type):
    """Extract score from different response formats based on task type."""
    try:
        # Try to find JSON blocks in the response
        json_blocks = re.findall(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if not json_blocks:
            # Try to find JSON without code blocks
            json_blocks = re.findall(r'\{[^{}]*\}', response_text)

        if task_type == "QA":
            # For QA tasks, look for Answer field or direct numerical answer
            for block in json_blocks:
                try:
                    parsed = json.loads(block)
                    if "Answer" in parsed:
                        # If answer is correct (5), give high score
                        answer = parsed["Answer"]
                        if str(answer).strip() == "5":
                            return 10.0
                        else:
                            return 0.0
                except:
                    continue
            # If no JSON, check if response starts with "5"
            if response_text.strip().startswith("5"):
                return 10.0
            return 0.0

        elif task_type == "EC":
            # For EC tasks, look for Corrected Answer
            for block in json_blocks:
                try:
                    parsed = json.loads(block)
                    if "Corrected Answer" in parsed:
                        # If corrected answer is 5, give score based on quality
                        corrected = str(parsed["Corrected Answer"]).strip()
                        if corrected == "5":
                            return 8.0  # Good correction
                        else:
                            return 2.0  # Incorrect correction
                except:
                    continue
            return 0.0

        elif task_type == "IP":
            # For IP tasks, look for Provided Approach or Steps
            for block in json_blocks:
                try:
                    parsed = json.loads(block)
                    if "Provided Approach" in parsed:
                        approach = parsed.get("Provided Approach", "")
                        # Check if approach has substance (steps or final_answer)
                        if isinstance(approach, dict):
                            if "steps" in approach and isinstance(approach["steps"], list) and len(approach["steps"]) > 0:
                                return 10.0
                            elif "final_answer" in approach:
                                return 8.0
                        elif isinstance(approach, str) and len(approach.strip()) > 20:
                            return 7.0
                        return 5.0
                    elif "Steps" in parsed:
                        steps = parsed.get("Steps", "")
                        if isinstance(steps, list) and len(steps) > 0:
                            return 10.0
                        elif isinstance(steps, str) and len(steps.strip()) > 20:
                            return 7.0
                        return 5.0
                except:
                    continue

            # Also check for steps-like content in response text
            if any(keyword in response_text.lower() for keyword in ["step", "first", "then", "finally", "approach"]):
                if len(response_text.strip()) > 50:
                    return 6.0
            return 0.0


    except Exception as e:
        print(f"Error extracting score from {task_type} response: {e}")
        return 0.0

    return 0.0


def analyze_evaluation_results(results_file):
    """Analyze evaluation results and identify best-performing task types."""
    if not os.path.exists(results_file):
        print(f"Results file {results_file} not found")
        return {}

    task_scores = {}
    scaffolding_scores_list = []
    answer_verification_stats = {"correct": 0, "incorrect": 0, "unknown": 0}

    with open(results_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                result = json.loads(line.strip())
                task_type = result.get('task_type', '')

                # Extract EduBench task scores
                scores = []
                if 'results' in result and isinstance(result['results'], list):
                    for model_result in result['results']:
                        if 'score' in model_result:
                            scores.append(model_result['score'])
                        else:
                            # Handle new response format without explicit score
                            response_text = model_result.get('response', '')
                            extracted_score = extract_score_from_response(response_text, task_type)
                            scores.append(extracted_score)

                # Use average score if multiple models, or the single score
                if scores:
                    avg_score = sum(scores) / len(scores)
                    if task_type not in task_scores:
                        task_scores[task_type] = []
                    task_scores[task_type].append(avg_score)

                # Extract scaffolding scores
                if 'scaffolding_evaluation' in result:
                    scaff_eval = result['scaffolding_evaluation']
                    if 'scaffolding_overall' in scaff_eval:
                        scaffolding_scores_list.append(scaff_eval['scaffolding_overall'] * 10)  # Convert 0-1 to 0-10

                # Extract answer verification
                if 'answer_verification' in result:
                    ans_verify = result['answer_verification']
                    is_correct = ans_verify.get('is_correct')
                    if is_correct is True:
                        answer_verification_stats["correct"] += 1
                    elif is_correct is False:
                        answer_verification_stats["incorrect"] += 1
                    else:
                        answer_verification_stats["unknown"] += 1

            except json.JSONDecodeError:
                continue

    # Calculate average scores for each task type
    avg_scores = {}
    for task_type, scores in task_scores.items():
        avg_scores[task_type] = sum(scores) / len(scores) if scores else 0

    print("\n" + "=" * 60)
    print("EVALUATION RESULTS ANALYSIS")
    print("=" * 60)

    print("\nEduBench Task Type Performance:")
    print("-" * 40)
    for task_type, avg_score in sorted(avg_scores.items(), key=lambda x: x[1], reverse=True):
        print(f"{task_type}: {avg_score:.2f}/10")

    if scaffolding_scores_list:
        avg_scaffolding = sum(scaffolding_scores_list) / len(scaffolding_scores_list)
        print(f"\nScaffolding Quality (V2 Evaluator):")
        print("-" * 40)
        print(f"Average Overall Score: {avg_scaffolding:.2f}/10")
        print(f"Questions Evaluated: {len(scaffolding_scores_list)}")

    total_verifications = sum(answer_verification_stats.values())
    if total_verifications > 0:
        print(f"\nAnswer Verification (GPT-5):")
        print("-" * 40)
        print(f"Correct: {answer_verification_stats['correct']} ({answer_verification_stats['correct']/total_verifications*100:.1f}%)")
        print(f"Incorrect: {answer_verification_stats['incorrect']} ({answer_verification_stats['incorrect']/total_verifications*100:.1f}%)")
        print(f"Unknown: {answer_verification_stats['unknown']} ({answer_verification_stats['unknown']/total_verifications*100:.1f}%)")

    print("=" * 60)

    return avg_scores


def extract_best_results(results_file, output_file=None, min_score_threshold=8.0):
    """Extract only the best results based on score threshold."""
    if not os.path.exists(results_file):
        print(f"Results file {results_file} not found")
        return []

    best_results = []
    task_type_counts = {}

    with open(results_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                result = json.loads(line.strip())
                task_type = result.get('task_type', '')

                # Extract score from nested results structure
                scores = []
                if 'results' in result and isinstance(result['results'], list):
                    for model_result in result['results']:
                        if 'score' in model_result:
                            scores.append(model_result['score'])
                        else:
                            # Handle new response format without explicit score
                            response_text = model_result.get('response', '')
                            extracted_score = extract_score_from_response(response_text, task_type)
                            scores.append(extracted_score)

                # Use average score if multiple models, or the single score
                if scores:
                    avg_score = sum(scores) / len(scores)
                    if avg_score >= min_score_threshold:
                        best_results.append(result)
                        task_type_counts[task_type] = task_type_counts.get(task_type, 0) + 1

            except json.JSONDecodeError:
                continue

    print(f"\nExtracted {len(best_results)} best results (score >= {min_score_threshold}):")
    for task_type, count in task_type_counts.items():
        print(f"  {task_type}: {count} results")

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in best_results:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
        print(f"Best results saved to: {output_file}")

    return best_results


def get_best_task_types(results_file, min_score_threshold=8.0):
    """Identify which task types consistently perform well."""
    avg_scores = analyze_evaluation_results(results_file)
    best_task_types = [task_type for task_type, score in avg_scores.items() if score >= min_score_threshold]

    print(f"\nBest performing task types (avg score >= {min_score_threshold}): {best_task_types}")
    return best_task_types


def evaluate_dataset_with_edubench(items, questions, output_file, normal_models, filter_task_types=None, request=None):
    tasks = []
    for idx, (item, question) in enumerate(zip(items, questions)):
        # Use filtered task types if provided, otherwise use all
        if filter_task_types:
            task_types = filter_task_types
            print(f"Using filtered task types: {task_types}")
        else:
            task_types = ["QA", "EC", "IP"]

        for task_type in task_types:
            question_text = item.get('information', {}).get('Question', '')

            task_data = {
                "question": question_text,
                "answer": question.answer,
                "explanation": question.explanation,
                "difficulty": question.difficulty or 'medium',
                "subject": item.get('information', {}).get('Subject', 'mathematics'),
                "grade": 3,
                "original_item_id": idx,
                "question_obj": question.model_dump() if hasattr(question, 'model_dump') else question.dict()
            }

            if task_type == "EC":
                task_data["original_answer"] = question.answer


            tasks.append((f"{idx}_{task_type}", task_type, task_data))

    if os.path.exists(output_file):
        os.remove(output_file)

    reasoning_models = []

    # Phase 1: Run scaffolding and verification in parallel
    print("Phase 1: Running scaffolding evaluation and answer verification in parallel...")
    unique_questions = {q.id if hasattr(q, 'id') else idx: q for idx, q in enumerate(questions)}
    scaffolding_results = {}
    answer_verification_results = {}

    with ThreadPoolExecutor(max_workers=20) as executor:
        scaffolding_futures = {}
        verification_futures = {}

        for qid, question in unique_questions.items():
            if request:
                scaffolding_futures[qid] = executor.submit(evaluate_question_scaffolding, question, request)

            question_text = getattr(question, 'question', '') or getattr(question, 'question_text', '')
            answer = getattr(question, 'answer', '')
            explanation = getattr(question, 'explanation', '')
            verification_futures[qid] = executor.submit(verify_answer_with_gpt4, question_text, answer, explanation)

        # Collect phase 1 results with error handling
        all_eval_futures = list(scaffolding_futures.values()) + list(verification_futures.values())
        with tqdm(total=len(all_eval_futures), desc="GPT Evaluations") as pbar:
            for future in as_completed(all_eval_futures):
                try:
                    for qid, fut in scaffolding_futures.items():
                        if fut == future:
                            scaffolding_results[qid] = future.result()
                            break
                    for qid, fut in verification_futures.items():
                        if fut == future:
                            answer_verification_results[qid] = future.result()
                            break
                except Exception as e:
                    print(f"Error in GPT evaluation: {e}")
                pbar.update(1)

    # Phase 2: Run EduBench tasks with completed scaffolding/verification results
    print("Phase 2: Running EduBench tasks in parallel...")
    with ThreadPoolExecutor(max_workers=20) as executor:
        task_futures = [
            executor.submit(
                process_single_task_with_scaffolding,
                tid,
                ttype,
                tdata,
                normal_models,
                reasoning_models,
                output_file,
                get_normal_answer,
                get_reasoning_answer,
                scaffolding_results,
                answer_verification_results
            ) for tid, ttype, tdata in tasks
        ]

        with tqdm(total=len(task_futures), desc="EduBench Tasks") as pbar:
            for future in as_completed(task_futures):
                try:
                    _ = future.result()
                except Exception as e:
                    print(f"Error in EduBench task: {e}")
                pbar.update(1)

    return scaffolding_results, answer_verification_results


def main():
    parser = argparse.ArgumentParser(description="Evaluate Grade 3 Mathematics using EduBench framework")
    parser.add_argument("--db_limit", type=int, default=200, help="Max questions from database")
    parser.add_argument("--db_grade", type=int, default=3, help="Grade level filter")
    parser.add_argument("--db_subject", type=str, default="mathematics", help="Subject filter")
    parser.add_argument("--db_hours", type=int, default=168, help="Hours ago to search (default: 1 week)")
    parser.add_argument("--output", type=str, default="src/evaluator/runs/undated/timestamp.jsonl", help="Output file")

    # New options for result analysis and filtering
    parser.add_argument("--analyze_results", type=str, help="Analyze existing results file")
    parser.add_argument("--extract_best", type=str, help="Extract best results from existing file")
    parser.add_argument("--min_score", type=float, default=8.0, help="Minimum score threshold for best results")
    parser.add_argument("--best_output", type=str, help="Output file for best results")
    parser.add_argument("--filter_tasks", action="store_true", help="Only run best-performing task types")
    parser.add_argument("--extracted_by_model", type=str, default="orchestrator-pipeline", help="Extracted by model")

    args = parser.parse_args()
    date = datetime.now().strftime("%d_%m_%Y")
    timestamp = datetime.now().strftime("%H-%M-%S")
    output_file = args.output.replace('undated', date).replace('timestamp', timestamp)

    # Handle result analysis mode
    if args.analyze_results:
        analyze_evaluation_results(args.analyze_results)
        return

    # Handle best results extraction mode
    if args.extract_best:
        best_output = args.best_output or args.extract_best.replace('.jsonl', '_best.jsonl')
        extract_best_results(args.extract_best, best_output, args.min_score)
        return

    # Normal evaluation mode
    req, resp = load_from_postgres(
        limit=args.db_limit,
        grade=args.db_grade,
        subject=args.db_subject,
        hours_ago=args.db_hours,
        extracted_by_model=args.extracted_by_model
    )
    items = [normalize_generated_question_to_edubench_qg(req, q) for q in resp.data]

    normal_models = ['EDU-Qwen2.5-7B']

    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)

    # Optionally filter for best task types
    filter_task_types = None
    if args.filter_tasks and os.path.exists(output_file):
        filter_task_types = get_best_task_types(output_file, args.min_score)
        if not filter_task_types:
            print("No best task types identified, using all task types")
            filter_task_types = None

    scaffolding_results, answer_verification_results = evaluate_dataset_with_edubench(items, resp.data, output_file, normal_models, filter_task_types, request=req)


if __name__ == "__main__":
    main()
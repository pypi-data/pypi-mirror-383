"""
Unified Evaluator: Combines v3.py and edubench.py evaluators.
Single clean function that takes request + questions and runs both evaluations.
"""

import sys
import uuid
import time
from pathlib import Path
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from datetime import datetime

# Add EduBench to path
edu_bench_path = Path(__file__).parent / "EduBench" / "code" / "evaluation"
sys.path.insert(0, str(edu_bench_path))

from src.dto.question_generation import GenerateQuestionsRequest, GeneratedQuestion, EvaluationModules
from src.evaluator.v3 import call_single_shot_evaluator
from src.evaluator.edubench import verify_answer_with_gpt4, get_normal_answer
from src.evaluator.EduBench.code.evaluation.evaluation import TASK_PROMPT_TEMPLATES


def evaluate_unified(
    request: GenerateQuestionsRequest,
    questions: List[GeneratedQuestion],
    task_types: List[str] = None,
    modules: EvaluationModules = None
) -> Dict[str, Any]:
    """
    Run configurable evaluations on 1-5 questions.

    Args:
        request: Question generation request
        questions: 1-5 generated questions
        task_types: DEPRECATED - EduBench task types (default: ["QA", "EC", "IP"])
        modules: Configuration for which modules to run (default: all enabled)

    Returns:
        Dict with v3_results, edubench_results, and answer_verification (conditionally included)
    """
    # Handle backward compatibility
    if modules is None:
        modules = EvaluationModules()

    # Prefer modules.edubench_tasks over deprecated task_types parameter
    effective_edubench_tasks = modules.edubench_tasks if modules.edubench_tasks is not None else task_types
    if effective_edubench_tasks is None:
        effective_edubench_tasks = ["QA", "EC", "IP"]

    results = {
        "v3_results": None,
        "edubench_results": None,
        "answer_verification": None
    }

    # Prepare futures based on module configuration
    all_futures = []
    v3_futures = {}
    verify_futures = {}
    edubench_futures = []

    # Single phase: Run enabled evaluations in parallel
    with ThreadPoolExecutor(max_workers=20) as executor:
        # Submit V3 evaluations if enabled
        if modules.v3_evaluation:
            results["v3_results"] = [None] * len(questions)
            v3_futures = {i: executor.submit(call_single_shot_evaluator, q, request, len(questions))
                          for i, q in enumerate(questions)}
            all_futures.extend(v3_futures.values())

        # Submit answer verifications if enabled
        if modules.answer_verification:
            results["answer_verification"] = [None] * len(questions)
            verify_futures = {i: executor.submit(verify_answer_with_gpt4, q.question, q.answer, q.explanation)
                              for i, q in enumerate(questions)}
            all_futures.extend(verify_futures.values())

        # Submit EduBench tasks if enabled
        if effective_edubench_tasks and len(effective_edubench_tasks) > 0:
            results["edubench_results"] = []
            for i, q in enumerate(questions):
                for task_type in effective_edubench_tasks:
                    edubench_futures.append(executor.submit(_run_edubench_task, i, task_type, q))
            all_futures.extend(edubench_futures)

        # Wait for all futures to complete (only enabled ones)
        if all_futures:
            with tqdm(total=len(all_futures), desc="Unified Evaluation") as pbar:
                for future in as_completed(all_futures):
                    pbar.update(1)

        # Collect results in order
        if modules.v3_evaluation:
            for i in range(len(questions)):
                results["v3_results"][i] = v3_futures[i].result()

        if modules.answer_verification:
            for i in range(len(questions)):
                results["answer_verification"][i] = verify_futures[i].result()

        if effective_edubench_tasks and len(effective_edubench_tasks) > 0:
            for future in edubench_futures:
                results["edubench_results"].append(future.result())

    return results


def _run_edubench_task(question_idx: int, task_type: str, question: GeneratedQuestion) -> Dict[str, Any]:
    """Run single EduBench task - just returns raw response like batch_edubench."""
    # Build prompt based on task type
    if task_type == "QA":
        prompt = TASK_PROMPT_TEMPLATES["QA"](question.question)
    elif task_type == "EC":
        prompt = TASK_PROMPT_TEMPLATES["EC"](question.question, question.answer)
    elif task_type == "IP":
        prompt = TASK_PROMPT_TEMPLATES["IP"](question.question)
    else:
        prompt = ""

    # Get raw response from model
    response = get_normal_answer(prompt, 'EDU-Qwen2.5-7B')

    # Return just like batch_edubench does - raw response, no scoring!
    return {
        "question_idx": question_idx,
        "task_type": task_type,
        "prompt": prompt,
        "response": response,
        "timestamp": datetime.now().isoformat()
    }


def evaluate_unified_with_response(
    request: GenerateQuestionsRequest,
    questions: List[GeneratedQuestion],
    task_types: List[str] = None,
    modules: EvaluationModules = None
) -> Dict[str, Any]:
    """
    High-level function that runs evaluation and formats clean API response.

    Args:
        request: Question generation request
        questions: Generated questions to evaluate
        task_types: DEPRECATED - Use modules.edubench_tasks instead
        modules: Configuration for which evaluation modules to run

    Returns a dict ready for API response with:
    - request_id
    - overall_scores
    - v3_scores (clean, optional)
    - answer_verification (clean, optional)
    - edubench_results (optional)
    - summary
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())

    # Handle backward compatibility
    if modules is None:
        modules = EvaluationModules()

    # Run core evaluation with module configuration
    results = evaluate_unified(request, questions, task_types, modules)

    # Calculate overall scores from v3 results (if enabled)
    v3_avg = 0.0
    if modules.v3_evaluation and results["v3_results"]:
        v3_overall_scores = []
        for v3_result in results["v3_results"]:
            if v3_result and "overall" in v3_result:
                v3_overall_scores.append(v3_result["overall"])
        v3_avg = sum(v3_overall_scores) / len(v3_overall_scores) if v3_overall_scores else 0.0

    # Calculate answer verification rate (if enabled)
    answer_correctness_rate = 0.0
    if modules.answer_verification and results["answer_verification"]:
        correct_answers = sum(1 for av in results["answer_verification"] if av and av.get("is_correct") == True)
        answer_correctness_rate = correct_answers / len(results["answer_verification"]) if results["answer_verification"] else 0.0

    # Extract only scores from v3_results (remove verbose details) if enabled
    clean_v3_scores = None
    if modules.v3_evaluation and results["v3_results"]:
        clean_v3_scores = []
        for v3_result in results["v3_results"]:
            if v3_result and "scores" in v3_result:
                # Convert EvaluationDimension enum keys to strings
                clean_scores = {
                    (k.value if hasattr(k, 'value') else str(k)): v
                    for k, v in v3_result["scores"].items()
                }
                clean_scores["overall"] = v3_result.get("overall", 0.0)
                clean_scores["recommendation"] = v3_result.get("recommendation", "revise")
                clean_v3_scores.append(clean_scores)

    # Simplify answer verification (keep only essential fields) if enabled
    clean_answer_verification = None
    if modules.answer_verification and results["answer_verification"]:
        clean_answer_verification = [
            {
                "is_correct": av.get("is_correct", False),
                "confidence": av.get("confidence", 0)
            }
            for av in results["answer_verification"]
        ]

    # EduBench results (if enabled)
    edubench_results = results.get("edubench_results") if results.get("edubench_results") else None

    # Build overall scores object
    overall_scores = {
        "total_questions": len(questions)
    }

    if modules.v3_evaluation:
        overall_scores["v3_average"] = v3_avg

    if modules.answer_verification:
        overall_scores["answer_correctness_rate"] = answer_correctness_rate

    if edubench_results:
        overall_scores["total_edubench_tasks"] = len(edubench_results)

    # Determine recommendation based on enabled metrics
    recommendation = "accept"
    if modules.v3_evaluation and v3_avg < 0.85:
        recommendation = "revise"
    if modules.answer_verification and answer_correctness_rate < 0.8:
        recommendation = "revise"

    # Build clean response
    return {
        "request_id": request_id,
        "overall_scores": overall_scores,
        "v3_scores": clean_v3_scores,
        "answer_verification": clean_answer_verification,
        "edubench_results": edubench_results,
        "summary": {
            "evaluation_time_seconds": time.time() - start_time,
            "questions_evaluated": len(questions),
            "recommendation": recommendation,
            "modules_enabled": {
                "v3_evaluation": modules.v3_evaluation,
                "answer_verification": modules.answer_verification,
                "edubench_tasks": modules.edubench_tasks if modules.edubench_tasks else []
            }
        }
    }

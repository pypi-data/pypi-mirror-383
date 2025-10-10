from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.wolfram.solve import wolfram_solve
from src.wolfram.types import WolframSolveRequest, WolframSolveResponse
import uvicorn
import os
import uuid
import logging
import json
import yaml
from dotenv import load_dotenv
import asyncio
import concurrent.futures
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Core imports
from src.dto.health import HealthResponse
from src.dto.question_generation import GenerateQuestionsRequest, GenerateQuestionResponse, SkillContext, EvaluationInfo, GeneratedQuestion, UnifiedEvaluationRequest, UnifiedEvaluationResponse

# Utils
from src.utils.ai_mapper import map_instructions_to_details
from src.utils.api_documentation import get_api_documentation

# New Modular System
from src.question_gen_v1.orchestrator import Orchestrator
from src.question_gen_v1.module_5 import Module5ScaffoldingGenerator
from src.config import Config

# LLM imports
from src.llms import solve_with_llm

load_dotenv()

# Get log level from Config, default to CRITICAL
log_level_value = getattr(logging, Config.LOG_LEVEL, logging.CRITICAL)

logging.getLogger().setLevel(log_level_value)
for name in logging.root.manager.loggerDict:
    logging.getLogger(name).setLevel(log_level_value)
logging.getLogger('src.orchestrator').setLevel(log_level_value)
logging.getLogger('src.llms').setLevel(log_level_value)

# API Key Authentication
security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key from Authorization header"""
    api_keys = Config.APP_API_KEYS.split(",")
    api_keys = [key.strip() for key in api_keys if key.strip()]
    
    if not api_keys:
        raise HTTPException(status_code=500, detail="API keys not configured")
    
    if credentials.credentials not in api_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return credentials.credentials

# Configure logging for performance tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler('performance.log')  # File output for analysis
    ]
)

# Note: LLM provider validation now handled by startup system
# Supports both OpenAI and Falcon providers

logger = logging.getLogger(__name__)

# Load OpenAPI spec from YAML file
def load_openapi_spec():
    """Load OpenAPI specification from YAML file"""
    try:
        # Get the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        openapi_path = os.path.join(project_root, "openapi.yaml")
        
        with open(openapi_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load openapi.yaml: {e}")
        return None

app = FastAPI()

# Override the OpenAPI schema with our custom YAML spec
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    # Try to load from YAML file first
    openapi_spec = load_openapi_spec()
    if openapi_spec:
        app.openapi_schema = openapi_spec
        return app.openapi_schema
    
    # Fallback to auto-generated if YAML fails
    openapi_schema = get_openapi(
        title="Incept Multilingual Generation API",
        version="2.0.0",
        description="API for generating educational questions with multilingual support",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Initialize generators  
orchestrator = Orchestrator()
module_5_generator = Module5ScaffoldingGenerator()

logger.info("🚀 SERVER READY: All systems initialized and ready for requests")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to Incept Question Generation Service"}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", service="incept-question-generation")


@app.get("/api/documentation")
async def api_documentation_endpoint():
    """
    Returns all possible keys and their explanations for the v1/generate_questions endpoint.
    """
    return get_api_documentation()


class CompletionsRequest(BaseModel):
    messages: List[Dict[str, str]]
    max_tokens: int = 8000
    provider: str = "falcon"
    language: Optional[str] = "english"


class CompletionsResponse(BaseModel):
    response: Any


@app.post("/completions", response_model=CompletionsResponse)
async def completions(request: CompletionsRequest, api_key: str = Depends(verify_api_key)):
    """
    Minimal completions endpoint that calls solve_with_llm.
    Supports providers: falcon, dspy, openai
    Supports languages: english, arabic, etc.
    """
    try:
        # Add language instruction to system message if specified
        messages = request.messages.copy()
        if request.language and request.language.lower() != "english":
            language_instruction = f"Please respond in {request.language}."
            # Check if there's a system message to append to
            system_msg_index = next((i for i, msg in enumerate(messages) if msg["role"] == "system"), None)
            if system_msg_index is not None:
                messages[system_msg_index]["content"] += f" {language_instruction}"
            else:
                # Add a new system message if none exists
                messages.insert(0, {"role": "system", "content": language_instruction})

        result = solve_with_llm(
            messages=messages,
            max_tokens=request.max_tokens,
            provider=request.provider.lower(),
            do_not_parse_json=True  # Get raw text response instead of parsing as JSON
        )
        return CompletionsResponse(response=result)
    except Exception as e:
        logger.error(f"Completions endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/wolfram/solve", response_model=WolframSolveResponse)
async def solve(request: WolframSolveRequest, api_key: str = Depends(verify_api_key)):
    """
    Solve a math problem using Wolfram|Alpha.
    """
    return wolfram_solve(request.question_text, request.subject, request.app_id)

@app.post("/v1/evaluate_unified", response_model=UnifiedEvaluationResponse)
async def evaluate_unified_endpoint(
    eval_request: UnifiedEvaluationRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    🎯 UNIFIED EVALUATION API

    Evaluate generated questions using unified evaluator (v3 + edubench + answer verification).

    Takes a request and 1-5 questions, returns comprehensive evaluation scores.

    ## Response Format:
    - overall_scores: Aggregate scores across all evaluators
    - v3_scores: Detailed scaffolding/DI compliance scores per question
    - answer_verification: GPT-4o answer correctness verification
    - summary: High-level summary statistics
    """
    try:
        logger.info(f"🔍 UNIFIED EVAL START: {len(eval_request.questions)} questions")

        # Import and call unified evaluator
        from src.evaluator.unified_evaluator import evaluate_unified_with_response

        # Run evaluation and get formatted response
        result = evaluate_unified_with_response(
            request=eval_request.request,
            questions=eval_request.questions,
            task_types=eval_request.task_types,
            modules=eval_request.modules
        )

        # Build response object
        response = UnifiedEvaluationResponse(**result)

        logger.info(f"⏱️ UNIFIED EVAL COMPLETE {result['request_id']}: "
                   f"V3 avg {result['overall_scores']['v3_average']:.2%}, "
                   f"Answer correctness {result['overall_scores']['answer_correctness_rate']:.2%} "
                   f"in {result['summary']['evaluation_time_seconds']:.2f}s")

        return response

    except Exception as e:
        logger.error(f"❌ UNIFIED EVAL FAILED: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unified evaluation failed: {str(e)}"
        )


@app.post(
    "/v1/generate_questions",
    response_model=GenerateQuestionResponse,
    summary="Generate Educational Questions",
    tags=["Question Generation"],
    responses={
        200: {"description": "Successfully generated questions"},
        400: {"description": "Invalid request parameters"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    }
)
async def generate_questions_v1(request: GenerateQuestionsRequest, api_key: str = Depends(verify_api_key)):
    """
    🎯 QUESTION GENERATION API

    Generate questions using the complete 5-module pipeline:

    Returns questions with comprehensive response format including:
    - Multiple question types (MCQ, fill-in)
    - Detailed explanations with step-by-step breakdown
    - Voiceover scripts for accessibility
    - Skill-based context integration
    - Personalized academic insights
    - Optional quality evaluation (when evaluate=true)

    ## Example Requests:

    ### Basic Request:
    ```json
    {
        "grade": 5,
        "instructions": "Generate questions about fractions",
        "count": 3,
        "difficulty": "medium"
    }
    ```

    ### With Evaluation:
    ```json
    {
        "grade": 5,
        "instructions": "Generate questions about fractions",
        "count": 3,
        "difficulty": "medium",
        "evaluate": true
    }
    ```

    ### With Skill Context & Evaluation:
    ```json
    {
        "grade": 7,
        "instructions": "Create algebra problems",
        "skill": {
            "id": "skill_123",
            "title": "Linear Equations",
            "unit_name": "Algebra",
            "lesson_title": "Solving Equations"
        },
        "evaluate": true
    }
    ```

    ## Evaluation Response (when evaluate=true):
    When evaluation is enabled, the response includes an 'evaluation' field:
    - overall_score: Quality score (0-1)
    - scores: Detailed scores by dimension
    - recommendations: Actionable improvement suggestions
    - report: Full human-readable evaluation report
    """
    import time
    api_start_time = time.time()
    
    try:
        request_id = str(uuid.uuid4())
        logger.info(f"🚀 V1 API START {request_id}: Grade {request.grade}, {request.count} questions, skill: {getattr(request.skill, 'title', None) if request.skill else None}")


        # Use AI mapper to intelligently extract educational details
        # educational_details = map_instructions_to_details(
        #     request.instructions, request.skill)
        # logger.info(f"AI mapped details: {educational_details}")

        # Generate complete questions with scaffolding using orchestrator
        # Prioritize explicit subject from request, then AI-mapped subject, then default to mathematics
        subject = request.subject  # or educational_details.get("subject", "mathematics")
        difficulty_setting = request.difficulty if request.difficulty != "mixed" else "medium"

        def combine_request_info(request):
            skill_title = request.skill.title if getattr(request, "skill", None) else None
            unit_name = request.skill.unit_name if getattr(request, "skill", None) else None
            lesson_title = request.skill.lesson_title if getattr(request, "skill", None) else None
            standard_description = getattr(request.skill, "standard_description", None) if getattr(request, "skill", None) else None
            instructions = getattr(request, "instructions", None)

            parts = [
                skill_title,
                unit_name,
                lesson_title,
                standard_description,
                instructions
            ]

            # Replace None with "None" and join
            return " | ".join(str(p) if p is not None else "None" for p in parts)

        # compile full skill title if unit or lesson provided
        skill_title = combine_request_info(request)
        provider_requested = request.model or "dspy"  # Default to DSPy for all operations
        
        # Run the async orchestrator in a separate thread with its own event loop
        # This prevents blocking the main FastAPI event loop for long-running operations
        def run_orchestrator_in_thread():
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    orchestrator.execute_complete_pipeline_with_scaffolding(
                        grade=request.grade,
                        subject=subject,
                        quantity=request.count or 5,
                        difficulty=difficulty_setting,
                        skill_title=skill_title,
                        language=request.language or 'arabic',
                        question_type=request.question_type or 'mcq',
                        provider_requested=provider_requested,
                        translate=request.translate,
                        existing_ratio=request.existing_ratio,
                        partial_match_threshold=request.partial_match_threshold
                    )
                )
            finally:
                loop.close()
        
        # Execute in thread pool to avoid blocking main event loop
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            generated_questions = await loop.run_in_executor(executor, run_orchestrator_in_thread)

        # Check if evaluation is requested
        if request.evaluate:
            # Create initial response structure for evaluation
            response_obj = GenerateQuestionResponse(
                data=generated_questions,
                request_id=request_id,
                total_questions=len(generated_questions),
                grade=request.grade
            )

            # Evaluate the response
            try:
                eval_start_time = time.time()
                logger.info(f"⏱️ EVALUATION START: request_id={request_id}")

                # Lazy import to avoid loading evaluator when not needed
                from src.evaluator.v3 import ResponseEvaluator
                from src.dto.question_generation import QuestionEvaluationDetail, SectionScore

                evaluator = ResponseEvaluator(parallel_workers=20)
                evaluation = evaluator.evaluate_response(request, response_obj)

                # Generate evaluation report
                evaluation_report = evaluator.generate_report(evaluation)

                # V3: Build question evaluations with section details
                question_evals = []
                for q_eval in evaluation.question_evaluations:
                    # Create section scores
                    question_section = None
                    if q_eval.question_section:
                        question_section = SectionScore(
                            section_score=q_eval.question_section.section_score,
                            issues=q_eval.question_section.issues,
                            strengths=q_eval.question_section.strengths,
                            recommendation=q_eval.question_section.recommendation
                        )

                    scaffolding_section = None
                    if q_eval.scaffolding_section:
                        scaffolding_section = SectionScore(
                            section_score=q_eval.scaffolding_section.section_score,
                            issues=q_eval.scaffolding_section.issues,
                            strengths=q_eval.scaffolding_section.strengths,
                            recommendation=q_eval.scaffolding_section.recommendation
                        )

                    image_section = None
                    if q_eval.image_section:
                        image_section = SectionScore(
                            section_score=q_eval.image_section.section_score,
                            issues=q_eval.image_section.issues,
                            strengths=q_eval.image_section.strengths,
                            recommendation=q_eval.image_section.recommendation
                        )

                    question_evals.append(QuestionEvaluationDetail(
                        question_id=q_eval.question_id,
                        overall_score=q_eval.overall_score,
                        recommendation=q_eval.recommendation,
                        question_section=question_section,
                        scaffolding_section=scaffolding_section,
                        image_section=image_section
                    ))

                # Create evaluation info with V3 section data
                eval_info = EvaluationInfo(
                    overall_score=evaluation.overall_score,
                    scores=evaluation.aggregate_scores,
                    recommendations=evaluation.recommendations,
                    report=evaluation_report,
                    section_scores=evaluation.compliance_report.get("section_scores"),
                    question_evaluations=question_evals
                )

                eval_time = time.time() - eval_start_time
                logger.info(f"⏱️ EVALUATION COMPLETE: Overall score {evaluation.overall_score:.2%} in {eval_time:.2f}s")

            except Exception as e:
                logger.warning(f"⚠️ Evaluation failed: {e}. Returning response with error.")
                # If evaluation fails, return response with error in evaluation
                eval_info = EvaluationInfo(
                    error=f"Evaluation failed: {str(e)}",
                    overall_score=None
                )

            # Create response with evaluation
            response = GenerateQuestionResponse(
                data=generated_questions,
                request_id=request_id,
                total_questions=len(generated_questions),
                grade=request.grade,
                evaluation=eval_info
            )
        else:
            # No evaluation requested, return simple response
            response = GenerateQuestionResponse(
                data=generated_questions,
                request_id=request_id,
                total_questions=len(generated_questions),
                grade=request.grade,
                evaluation=None
            )


        api_total_time = time.time() - api_start_time
        logger.info(f"⏱️ API COMPLETE: {len(generated_questions)} questions generated in {api_total_time:.2f}s total (request_id={request_id})")
        return response

    except Exception as e:
        logger.error(f"V1 Question generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Question generation failed: {str(e)}"
        )



if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)

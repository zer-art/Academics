from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import GEMINI, GEMINI_MODEL
from .prompt import PROMPT_TEMPLATE
from langchain.prompts import PromptTemplate
import logging

logger = logging.getLogger(__name__)


try:
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=GEMINI,
        temperature=0.2,
    )
except Exception as e:
    llm = None
    logger.warning(f"Failed to initialize Gemini LLM client: {e}")


def generate_interview_questions(role: str):
    """Generate interview questions for a given role using the configured LLM."""
    if llm is None:
        raise RuntimeError(
            "LLM client is not configured. Set GEMINI/GEMINI_API_KEY and ensure the model name is valid."
        )

    prompt_template = PromptTemplate(
        input_variables=["role"],
        template=PROMPT_TEMPLATE,
    )

    formatted_prompt = prompt_template.format(role=role)

    response = llm(formatted_prompt)
    return response

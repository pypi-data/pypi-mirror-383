from pydantic import BaseModel, Field
import instructor
from typing import List
from litellm import completion

from .utils import get_api_key, parse_api
from .logging_utils import logger


class ScoreEntry(BaseModel):
    celltype: str = Field(..., description="The candidate cell type name.")
    score: float = Field(..., description="Confidence score for the cell type.")


class ScoreInfo(BaseModel):
    score_thinking: str = Field(
        description="LLM thinking content for the scoring step; may be under 'thinking' tags or sections."
    )
    score_ls: List[ScoreEntry] = Field(
        ..., description="List of cell type score entries."
    )


def extract_score(content, provider, model, base_url):
    provider, model, base_url = parse_api(provider, model, base_url)
    API_KEY = get_api_key(provider)
    client = instructor.from_litellm(completion)
    logger.info(
        "Extracting structured scores using provider '%s' and model '%s'.",
        provider or "default",
        model or "default",
    )
    resp = client.chat.completions.create(
        model=model,
        api_key=API_KEY,
        api_base=base_url,
        max_tokens=4000,
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ],
        response_model=ScoreInfo,
    )
    logger.info("Structured score extraction complete.")
    return resp

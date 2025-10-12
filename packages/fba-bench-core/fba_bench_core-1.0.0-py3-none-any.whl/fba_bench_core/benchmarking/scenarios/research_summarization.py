"""Research summarization scenario."""

import random
from typing import Any

from pydantic import BaseModel, Field

from .base import BaseScenario


class ResearchSummarizationConfig(BaseModel):
    """Configuration for research summarization scenario."""

    num_docs: int = Field(default=5, gt=0, description="Number of documents")
    max_tokens: int = Field(
        default=200, gt=0, description="Maximum tokens per document"
    )
    focus_keywords: list[str] = Field(
        default=["research", "findings", "methodology"],
        description="Keywords to focus on",
    )
    noise_probability: float = Field(
        default=0.1, ge=0.0, le=0.5, description="Probability of noise"
    )


class ResearchSummarizationScenario(BaseScenario):
    """
    This class now correctly implements the modern BaseScenario API.
    """

    def __init__(self, params: dict[str, Any] | None = None):
        """
        The constructor now only accepts a `params` dictionary.
        """
        super().__init__(params)
        self.config = ResearchSummarizationConfig(**(self.params or {}))

    async def run(self, runner: Any, payload: dict[str, Any]) -> dict[str, Any]:
        """
        All scenario logic is now contained within this single method.
        """
        seed = payload.get("seed", 0)
        rng = random.Random(seed)

        # --- 1. Setup Phase ---
        documents = self.setup_documents(rng)

        # --- 2. Execution Loop ---
        summaries = []
        for doc in documents:
            prompt = self.create_prompt(doc)
            response = await runner.process(prompt)
            summary_text = (
                response.get("content", str(response))
                if isinstance(response, dict)
                else str(response)
            )
            summaries.append(
                {
                    "doc_id": doc["id"],
                    "summary": summary_text,
                    "original_content": doc["content"],
                }
            )

        # --- 3. Evaluation and Results ---
        metrics = self.evaluate_summaries(summaries)

        return {
            "metrics": metrics,
            "summaries": [s["summary"] for s in summaries],
            "documents": [d["content"] for d in documents],
        }

    def setup_documents(self, rng: random.Random) -> list[dict[str, Any]]:
        documents = []
        for i in range(self.config.num_docs):
            base_content = f"Research paper {i + 1}: This study explores key findings in {', '.join(self.config.focus_keywords)}. "
            base_content += f"The methodology involved analysis with approximately {self.config.max_tokens} tokens of data. "

            if rng.random() < self.config.noise_probability:
                base_content += (
                    "Irrelevant detail: weather conditions during the study. "
                )

            content = base_content * (
                self.config.max_tokens // len(base_content.split()) + 1
            )
            content = " ".join(content.split()[: self.config.max_tokens // 4])

            documents.append({"id": i, "content": content})
        return documents

    def create_prompt(self, doc: dict[str, Any]) -> str:
        return (
            f"Summarize the following research paper, focusing on the key {', '.join(self.config.focus_keywords)}.\n\n"
            f"Paper content:\n{doc['content']}\n\n"
            f"Provide a concise summary of 100-200 words highlighting the main findings and methodology."
        )

    def evaluate_summaries(self, summaries: list[dict[str, Any]]) -> dict[str, Any]:
        if not summaries:
            return {
                "average_quality_score": 0.0,
                "keyword_coverage": 0.0,
                "conciseness_score": 0.0,
                "total_documents": 0,
            }

        total_coverage = 0.0
        total_conciseness = 0.0
        num_keywords = len(self.config.focus_keywords)
        if num_keywords == 0:
            num_keywords = 1

        for summary_info in summaries:
            summary_lower = summary_info["summary"].lower()
            keywords_lower = [kw.lower() for kw in self.config.focus_keywords]

            coverage = (
                sum(1 for kw in keywords_lower if kw in summary_lower) / num_keywords
            )
            total_coverage += coverage

            original_words = len(summary_info["original_content"].split())
            summary_words = len(summary_info["summary"].split())
            conciseness = 1.0 if 0.1 <= summary_words / original_words <= 0.3 else 0.5

            total_conciseness += conciseness

        avg_coverage = total_coverage / len(summaries)
        avg_conciseness = total_conciseness / len(summaries)
        avg_quality = (avg_coverage + avg_conciseness) / 2

        return {
            "average_quality_score": round(avg_quality, 4),
            "keyword_coverage": round(avg_coverage, 4),
            "conciseness_score": round(avg_conciseness, 4),
            "total_documents": len(summaries),
        }

import json
from typing import Any


class GeminiNotConfiguredError(RuntimeError):
    pass


class GeminiService:
    def __init__(self, api_key: str | None, model: str):
        self.api_key = api_key
        self.model = model

    def generate_answer(self, question: str, data_context: dict[str, Any]) -> str:
        if not self.api_key:
            raise GeminiNotConfiguredError("GEMINI_API_KEY is not configured.")

        from google import genai

        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(
            model=self.model,
            contents=self._build_prompt(question, data_context),
        )
        return (response.text or "").strip()

    def _build_prompt(self, question: str, data_context: dict[str, Any]) -> str:
        context_json = json.dumps(data_context, ensure_ascii=True, default=str)
        return (
            "You are NEXUS AI, a concise data assistant for Pacific agriculture yield data.\n"
            "Answer only from the dataset context provided below. If the context does not contain "
            "enough evidence, say what is missing and suggest a more specific question.\n"
            "Use country, product, year, unit, and trend details when available. Do not invent exact "
            "numbers, causes, or climate explanations that are not supported by the context.\n"
            "Keep the answer friendly, useful, and under 180 words unless the user asks for more detail.\n\n"
            f"User question:\n{question}\n\n"
            f"Dataset context JSON:\n{context_json}"
        )

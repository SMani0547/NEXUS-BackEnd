import json
from typing import Any


class GeminiNotConfiguredError(RuntimeError):
    pass


class GeminiService:
    def __init__(self, api_key: str | None, model: str):
        self.api_key = api_key
        self.model = model

    def generate_answer(self, question: str, data_context: dict[str, Any]) -> str:
        response = self.generate_response(question, data_context)
        return response["answer"]

    def generate_response(self, question: str, data_context: dict[str, Any]) -> dict[str, Any]:
        if not self.api_key:
            raise GeminiNotConfiguredError("GEMINI_API_KEY is not configured.")

        from google import genai

        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(
            model=self.model,
            contents=self._build_prompt(question, data_context),
        )
        return self._parse_response(response.text or "")

    def _build_prompt(self, question: str, data_context: dict[str, Any]) -> str:
        context_json = json.dumps(data_context, ensure_ascii=True, default=str)
        return (
            "You are NEXUS AI, a concise data assistant for Pacific agriculture yield data.\n"
            "Answer only from the dataset context provided below. If the context does not contain "
            "enough evidence, say what is missing and suggest a more specific question.\n"
            "Use country, product, year, unit, and trend details when available. Do not invent exact "
            "numbers, causes, or climate explanations that are not supported by the context.\n"
            "Keep the answer friendly, useful, and under 180 words unless the user asks for more detail.\n\n"
            "Return only JSON in this shape:\n"
            "{\"answer\":\"...\",\"suggested_questions\":[\"...\",\"...\",\"...\"]}\n"
            "The suggested_questions should be natural follow-up questions based on the user's question "
            "and the available dataset context.\n\n"
            f"User question:\n{question}\n\n"
            f"Dataset context JSON:\n{context_json}"
        )

    def _parse_response(self, text: str) -> dict[str, Any]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
            cleaned = cleaned.removesuffix("```").strip()

        try:
            data = json.loads(cleaned)
            answer = str(data.get("answer", "")).strip()
            suggestions = data.get("suggested_questions", [])
            if not isinstance(suggestions, list):
                suggestions = []
            return {
                "answer": answer or cleaned,
                "suggested_questions": [str(item).strip() for item in suggestions if str(item).strip()][:4],
            }
        except json.JSONDecodeError:
            return {"answer": cleaned, "suggested_questions": []}

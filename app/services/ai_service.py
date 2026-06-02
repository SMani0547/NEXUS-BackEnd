from app.services.analytics_service import AnalyticsService


class AIService:
    def __init__(self, analytics: AnalyticsService):
        self.analytics = analytics

    def answer(self, question: str) -> dict:
        context = self.analytics.dataset_context(question)
        matched_countries = context["matched_countries"]
        matched_products = context["matched_products"]

        parts = ["Nexus AI is in placeholder mode."]
        if matched_countries:
            parts.append(f"I found dataset context for: {', '.join(matched_countries)}.")
        if matched_products:
            parts.append(f"I found product context for: {', '.join(matched_products)}.")
        if not matched_countries and not matched_products:
            parts.append("Ask about a country, product, yield trend, or comparison available in the dataset.")

        return {
            "answer": " ".join(parts),
            "note": "Gemini 2.5 Flash integration will be added later. For now, this endpoint only prepares dataset-aware context.",
            "data_context": context,
        }


"""
src/analyzer.py
Connects to the Gemini API and enforces Pydantic structured output.
"""

import os
import logging
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Silence the Google GenAI SDK logging warnings
logging.getLogger("google").setLevel(logging.ERROR)
logging.getLogger("google.genai").setLevel(logging.ERROR)


# 1. Define Pydantic models for structured LLM output
class KeyInsight(BaseModel):
    title: str = Field(description="Short, punchy headline for the insight")
    observation: str = Field(
        description="Factual data observation based on provided statistics"
    )
    business_impact: str = Field(
        description="Why this insight matters for the business"
    )


class DataAnomaly(BaseModel):
    metric: str = Field(
        description="Name of the metric or column where anomaly occurred"
    )
    finding: str = Field(
        description="Description of the outlier, gap, or unexpected value"
    )
    risk_level: str = Field(description="Risk assessment: High, Medium, or Low")


class ExecutiveReport(BaseModel):
    summary: str = Field(
        description="2-sentence executive summary of overall data performance"
    )
    key_insights: list[KeyInsight] = Field(
        description="List of 2-3 critical insights"
    )
    anomalies: list[DataAnomaly] = Field(
        description="List of detected anomalies or outliers"
    )
    recommended_actions: list[str] = Field(
        description="3 clear, actionable steps for management"
    )


# 2. Main Analyzer Class
class DataAnalyzer:
    """Connects to Gemini API and generates structured analysis from data statistics."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing from environment variables."
            )
        self.client = genai.Client(api_key=api_key)

    def analyze(self, stats: dict) -> ExecutiveReport:
        """Sends statistics to Gemini and validates the JSON response against ExecutiveReport schema."""
        prompt = f"""
        You are a Lead Business & Data Analyst. Analyze the following summary statistics extracted from a dataset.
        Generate a concise, high-impact executive report based strictly on these metrics.

        Data Statistics:
        {stats}
        """

        # Enforce structured output matching our Pydantic schema
        response = self.client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExecutiveReport,
                temperature=0.2,
            ),
        )

        # Type Guard: Ensure response.text exists before passing to Pydantic
        if not response.text:
            raise ValueError(
                "Gemini API returned an empty response or was blocked by safety filters."
            )

        # Parse and validate returned JSON into Pydantic model
        return ExecutiveReport.model_validate_json(response.text)
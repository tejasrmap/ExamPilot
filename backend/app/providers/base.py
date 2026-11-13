from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class ConfidenceModel(BaseModel):
    level: str = Field(description="high, medium, or low")
    reason: str = Field(description="Educational reasoning explaining certainty/uncertainty")

class OptionIdentity(BaseModel):
    id: str = Field(description="Unique internal option identifier e.g. opt_1")
    text: str = Field(description="Extracted option text")
    original_label: Optional[str] = Field(default=None, description="Original visible label, e.g. 'A', '1', or None if unlettered")
    internal_label: str = Field(description="Internal model key e.g. A, B, C, D")
    source_order: int = Field(description="1-based original position in source question")
    confidence: Optional[float] = Field(default=None, description="OCR confidence for this option")
    is_user_edited: bool = Field(default=False, description="Whether user edited the option text")

class QuestionAnalysisResult(BaseModel):
    question: str
    suggested_answer: str = Field(description="Internal key of selected option, e.g. A, B, C, D")
    answer_text: str = Field(description="Full text of the selected correct answer")
    original_label: Optional[str] = Field(default=None, description="Original visible option label, if one existed in source")
    source_position: Optional[int] = Field(default=None, description="1-based source position of the correct answer")
    explanation: str = Field(description="Pedagogical explanation of the solution")
    option_analysis: Dict[str, str] = Field(description="Breakdown of why each individual option is correct or incorrect")
    confidence: ConfidenceModel
    subject: str = Field(default="General", description="Academic subject or domain")
    subject_confidence: float = Field(default=0.0, description="Confidence in subject classification (0.0 to 1.0)")
    curriculum_confidence: float = Field(default=0.0, description="Confidence in curriculum standard grounding (0.0 to 1.0)")
    evidence: Optional[str] = Field(default=None, description="Authoritative curriculum evidence/standard definition supporting answer")
    is_ambiguous: bool = Field(default=False, description="Flagged true if question is ambiguous, contradictory, or duplicate")
    ambiguity_details: Optional[List[str]] = Field(default=None, description="Specific ambiguity issues detected")
    needs_review: bool = Field(default=False, description="Flagged true if question requires human review")
    structured_options: Optional[List[OptionIdentity]] = Field(default=None, description="Preserved option identity metadata")
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float = 0.0

class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    supports_vision: bool = False
    context_window: int = 128000
    input_cost_per_million: float = 0.0
    output_cost_per_million: float = 0.0

class BaseAIProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the identifier name (e.g., 'openai', 'gemini', 'anthropic', 'openrouter')"""
        pass

    @abstractmethod
    async def validate_key(self, api_key: str) -> bool:
        """Test if the provided API key is valid against the provider endpoint."""
        pass

    @abstractmethod
    async def list_models(self, api_key: Optional[str] = None) -> List[ModelInfo]:
        """Return available models for this provider."""
        pass

    @abstractmethod
    async def generate_analysis(
        self,
        api_key: str,
        model: str,
        question_text: str,
        options: Dict[str, str],
        subject: Optional[str] = None,
        context_material: Optional[str] = None,
        structured_options: Optional[List[Dict[str, Any]]] = None
    ) -> QuestionAnalysisResult:
        """Analyzes an MCQ and returns strict Pydantic QuestionAnalysisResult."""
        pass

    @abstractmethod
    async def chat(
        self,
        api_key: str,
        model: str,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Chat generation returning assistant text and token usage."""
        pass


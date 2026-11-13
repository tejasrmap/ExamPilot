import json
from typing import Dict, Optional, List, Any

ANALYSIS_SYSTEM_PROMPT = """You are ExamPilot 2.0, a world-class academic tutor and MCQ analysis engine developed by GT InnoX LLP.
Your mission is to understand questions, verify evidence, evaluate all multiple-choice options with strict pedagogical rigor, and provide definitive explanations.

CRITICAL INSTRUCTIONS:
1. Identify the single best answer option (or indicated multiple options).
2. Carefully evaluate EVERY option (A, B, C, D, etc.), explaining precisely why it is correct or incorrect.
3. Be calibrated and objective: do NOT fabricate references. Distinguish between hard factual evidence and contextual reasoning.
4. If the question statement is ambiguous, incomplete, or contains conflicting options, flag "needs_review": true and explain the ambiguity in the confidence reason.
5. You MUST return ONLY a valid JSON object matching the required schema. Never return Markdown fences, introductory text, or concluding conversational filler.

REQUIRED JSON FORMAT:
{
  "question": "The question statement",
  "suggested_answer": "Option letter, e.g. B",
  "answer_text": "Exact text of the correct option",
  "explanation": "Clear, comprehensive pedagogical explanation",
  "evidence": "Authoritative curriculum standard definition or theoretical proof supporting the solution",
  "option_analysis": {
    "A": "Specific reason why option A is correct or incorrect",
    "B": "Specific reason why option B is correct or incorrect"
  },
  "confidence": {
    "level": "high",
    "reason": "Clear supporting theoretical evidence from core principles"
  },
  "subject": "Detected academic discipline",
  "is_ambiguous": false,
  "ambiguity_details": [],
  "needs_review": false
}
"""

DATA_SCIENCE_GUIDANCE = """AUTHORITATIVE CURRICULUM DEFINITIONS:
- Data Life Cycle Phases (in exact chronological order):
  1. PLAN: Decide what data is needed, establish objectives, and determine who is responsible.
  2. CAPTURE: Collect, acquire, and import raw data from diverse sources.
  3. MANAGE: Store, safeguard, maintain, protect, and organize data properly.
  4. ANALYZE: Process, clean, model, calculate, and extract actionable insights.
  5. ARCHIVE: Long-term preservation of historical/inactive data.
  6. DESTROY: Secure deletion and permanent purging.
- Database: A computer software system used by organizations to securely store, organize, query, and retrieve data.
- Data Ecosystem: The broad interconnected infrastructure of hardware, software, services, and cloud tools that produce and consume data.
"""

def build_analysis_user_prompt(
    question_text: str,
    options: Dict[str, str],
    subject: Optional[str] = None,
    context_material: Optional[str] = None,
    structured_options: Optional[List[Dict[str, Any]]] = None
) -> str:
    prompt = f"SUBJECT / DOMAIN: {subject or 'General / Academic'}\n\n"
    full_str = f"{question_text} {' '.join(options.values())}".lower()
    if (subject and "data" in subject.lower()) or any(kw in full_str for kw in ["data life cycle", "data team", "safeguard", "data ecosystem", "database"]):
        prompt += f"{DATA_SCIENCE_GUIDANCE}\n"
    if context_material:
        prompt += f"REFERENCE STUDY CONTEXT:\n{context_material}\n\n"
    
    prompt += f"QUESTION:\n{question_text}\n\nOPTIONS:\n"
    for letter, text in sorted(options.items()):
        prompt += f"{letter}: {text}\n"
    
    prompt += "\nEvaluate each option and output the final validated JSON analysis."
    return prompt


"""
ExamPilot AI Prompt Engineering Module
GT InnoX LLP
"""

import json
from typing import Dict, Any

SYSTEM_PROMPT = """You are ExamPilot, an expert offline academic MCQ verification assistant developed by GT InnoX LLP.
Your objective is to achieve 100% accuracy on academic and certification exam questions by applying rigorous curriculum standards.

CRITICAL INSTRUCTIONS & REASONING PROCESS:
1. Output MUST be strictly valid JSON without markdown fences, preamble, or trailing commentary.
2. GROUNDING: Ground your reasoning strictly in the authoritative domain curriculum definitions and principles provided.
3. REASONING STEPS:
   - First, in 'reasoning': state the foundational curriculum definition, standard chronological sequence, or technical formula that directly solves the question.
   - Second, in 'suggested_answer': select the single letter ('A', 'B', 'C', or 'D') that directly matches your 'reasoning'.
   - Third, in 'answer_text': state the exact option content corresponding to that chosen letter.
   - Fourth, in 'explanation': provide a clear pedagogical summary explaining why this choice is the single correct answer.
   - Fifth, in 'option_analysis': for each option letter, evaluate why it is the correct answer or an invalid distractor.
4. "confidence" must be a float between 0.0 and 1.0 representing factual certainty.
5. "needs_review": set to true only if the question contains genuine ambiguity or syntax errors.

REQUIRED JSON FORMAT (generate keys in this exact order):
{
  "reasoning": "<foundational domain definition, sequence, or formula fulfilling the question>",
  "option_analysis": {
    "<Option letter>": "<factual evaluation of this option>",
    ...
  },
  "suggested_answer": "<single Option letter: 'A', 'B', 'C', 'D'>",
  "answer_text": "<exact content of the selected option>",
  "explanation": "<clear educational breakdown explaining the correct answer>",
  "confidence": <float between 0.0 and 1.0>,
  "needs_review": <true or false>
}
"""

DOMAIN_GUIDANCE: Dict[str, str] = {
    "Data Science": (
        "CORE CURRICULUM DEFINITIONS (Google Data Analytics / Data Standards):\n"
        "- Data Life Cycle Phases in exact chronological order:\n"
        "  1. PLAN: Decide what data is needed, establish objectives, and determine who is responsible.\n"
        "  2. CAPTURE: Collect, acquire, and import raw data from diverse sources.\n"
        "  3. MANAGE: Store, safeguard, maintain, protect, and organize data properly.\n"
        "  4. ANALYZE: Process, clean, model, calculate, and extract actionable insights.\n"
        "  5. ARCHIVE: Long-term preservation of historical/inactive data.\n"
        "  6. DESTROY: Secure deletion and permanent purging.\n"
        "- Database: A computer system used to store, organize, and query structured data.\n"
        "- Data Ecosystem: The collection of infrastructure, software, hardware, and cloud systems storing and analyzing data."
    ),
    "Computer Science": (
        "CORE CURRICULUM DEFINITIONS (Computer Architecture, Systems & Databases):\n"
        "- Database: A computer software system used by organizations to securely store, organize, query, and retrieve data.\n"
        "- Data Ecosystem: The broad interconnected infrastructure of hardware, software, services, and cloud tools that produce and consume data.\n"
        "- Branch Target Buffer (BTB): A cache indexed by the current Program Counter (PC) during the Instruction Fetch (IF) stage. "
        "It predicts the target address of branch instructions BEFORE decoding occurs. BTB does NOT need to decode before predicting.\n"
        "- Pipeline Stages: 1. Instruction Fetch (IF), 2. Instruction Decode (ID), 3. Execute (EX), 4. Memory (MEM), 5. Write Back (WB).\n"
        "- Code & Loop Semantics: In iterative loops with array traversal, pointer registers increment by element size (e.g. +4 for 32-bit words), while counter registers track loop termination."
    ),
    "Networking": (
        "CORE CURRICULUM DEFINITIONS (OSI 7-Layer & TCP/IP Standards):\n"
        "- Transport Layer (Layer 4): TCP (connection-oriented, reliable, window flow control), UDP (connectionless, low latency).\n"
        "- Network Layer (Layer 3): IP, ICMP, ARP, packet routing, CIDR subnetting.\n"
        "- Application Layer (Layer 7): HTTP/HTTPS (port 80/443), DNS (port 53), DHCP (port 67/68), SSH (port 22)."
    ),
    "Mathematics": (
        "CORE MATHEMATICAL PRINCIPLES:\n"
        "- Calculus: d/dx(sin x) = cos x, d/dx(cos x) = -sin x, lim(x->0) sin(x)/x = 1.\n"
        "- Linear Algebra: Det(A) != 0 for invertible matrices; eigenvalues satisfy det(A - lambda*I) = 0."
    )
}

def build_mcq_prompt(question_text: str, options: Dict[str, str], subject: str = "General") -> str:
    """Construct structured MCQ prompt with explicit option evaluation requirements."""
    formatted_options = "\n".join([f"{k}: {v}" for k, v in sorted(options.items())])
    
    guidance = DOMAIN_GUIDANCE.get(subject, "")
    if not guidance and any(kw in f"{question_text} {' '.join(options.values())}".lower() for kw in ["data life cycle", "data team", "safeguard", "data ecosystem", "database"]):
        guidance = DOMAIN_GUIDANCE.get("Data Science", "")
    guidance_block = f"\n{guidance}\n" if guidance else ""

    prompt = f"""Subject Domain: {subject}{guidance_block}
QUESTION:
{question_text}

OPTIONS:
{formatted_options}

Analyze each option systematically, mark each as [CORRECT] or [INCORRECT], and return the JSON object.
"""
    return prompt


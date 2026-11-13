"""
ExamPilot 2.0 — Comprehensive OCR and MCQ Reliability Regression Test Suite
GT InnoX LLP — Understand Questions. Learn the Answers.

Tests:
1. Multi-line fill-in-the-blank questions (Coursera Q2 reproduction)
2. Instruction headers containing 'Fill in the blank'
3. Questions ending in auxiliary verbs or prepositions
4. Unlettered radio-button options (Coursera-style)
5. OCR artifacts such as 'c)' on unlettered options
6. Variable option counts (2, 3, 4, 5, 6 options)
7. Questions containing programming instructions and assembly code
8. Option identity preservation (id, text, original_label, source_order, confidence, is_user_edited)
9. Curriculum grounding across all 6 phases (Plan, Capture, Manage, Analyze, Archive, Destroy)
10. Insufficient evidence / non-Data Science negative tests
11. Dual-architecture equivalence (Desktop vs SaaS Backend)
"""

import pytest
from desktop.core.question_parser import QuestionParser as DesktopParser
from backend.app.services.parser import QuestionParser as BackendParser

from desktop.ai.domain_detector import detect_domain as desktop_detect_domain
from desktop.ai.domain_detector import detect_domain_with_details as desktop_detect_details
from backend.app.services.domain_detector import detect_domain as backend_detect_domain
from backend.app.services.domain_detector import detect_domain_with_details as backend_detect_details

from desktop.ai.prompts import build_mcq_prompt as desktop_build_prompt
from backend.app.providers.prompt_builder import build_analysis_user_prompt as backend_build_prompt

# ---------------------------------------------------------------------------
# FIXTURE 1: Multi-line Fill-in-the-blank (Original Coursera Q2 Defect Reproduction)
# ---------------------------------------------------------------------------
def test_reproduce_multiline_fill_in_the_blank_coursera():
    """
    Original Defect: '2. Fill in the blank: During the ___ phase, data teams decide what kind of data is needed...'
    was split after line 0, turning 'phase, data teams decide...' into Option A and 'responsible for it' into Option B.
    Regression Requirement: The entire statement must remain in the question.
    """
    text = (
        "2. Fill in the blank: During the\n"
        "___ phase, data teams decide what kind of data is needed and who will be\n"
        "responsible for it.\n"
        "analyze\n"
        "planning\n"
        "capture\n"
        "manage"
    )
    for ParserCls in [DesktopParser, BackendParser]:
        parser = ParserCls()
        result = parser.parse_from_text(text)
        
        # Verify question statement integrity
        q = result["question"]
        assert "During the ___ phase, data teams decide" in q
        assert "who will be responsible for it" in q
        
        # Verify options are NOT question fragments
        assert len(result["options"]) == 4
        assert result["options"]["A"] == "analyze"
        assert result["options"]["B"] == "planning"
        assert result["options"]["C"] == "capture"
        assert result["options"]["D"] == "manage"
        
        # Option identity verification
        assert result["has_original_labels"] is False
        assert len(result["structured_options"]) == 4
        assert result["structured_options"][0]["original_label"] is None
        assert result["structured_options"][0]["source_order"] == 1
        assert result["structured_options"][1]["text"] == "planning"
        assert result["structured_options"][1]["original_label"] is None
        assert result["structured_options"][1]["source_order"] == 2

# ---------------------------------------------------------------------------
# FIXTURE 2: Instruction Headers Containing 'Fill in the blank'
# ---------------------------------------------------------------------------
def test_instruction_header_standalone():
    """
    Line 0 is purely an instruction prefix: 'Fill in the blank:'
    The actual sentence follows on line 1.
    """
    text = (
        "Fill in the blank:\n"
        "A relational database organizes records into structured tables with rows and ____.\n"
        "columns\n"
        "indices\n"
        "sockets\n"
        "threads"
    )
    for ParserCls in [DesktopParser, BackendParser]:
        parser = ParserCls()
        result = parser.parse_from_text(text)
        
        assert "organizes records into structured tables with rows and ____" in result["question"]
        assert len(result["options"]) == 4
        assert result["options"]["A"] == "columns"
        assert result["options"]["B"] == "indices"
        assert result["options"]["C"] == "sockets"
        assert result["options"]["D"] == "threads"

# ---------------------------------------------------------------------------
# FIXTURE 3: Questions Ending in Auxiliary Verbs or Prepositions
# ---------------------------------------------------------------------------
def test_questions_ending_in_dangling_auxiliary_or_preposition():
    """
    Question sentence lines terminating with 'who will be', 'of', 'to', 'in', 'for'
    must not cause premature truncation into answer options.
    """
    text = (
        "In modern cloud architectures, the primary mechanism responsible for\n"
        "routing incoming HTTPS requests to healthy backend replicas is known as\n"
        "Load Balancer\n"
        "Reverse Compiler\n"
        "Circuit Breaker\n"
        "DMA Controller"
    )
    for ParserCls in [DesktopParser, BackendParser]:
        parser = ParserCls()
        result = parser.parse_from_text(text)
        
        assert "routing incoming HTTPS requests to healthy backend replicas is known as" in result["question"]
        assert len(result["options"]) == 4
        assert result["options"]["A"] == "Load Balancer"
        assert result["options"]["D"] == "DMA Controller"

# ---------------------------------------------------------------------------
# FIXTURE 4: Unlettered Radio-Button Options (Never Invent Letters)
# ---------------------------------------------------------------------------
def test_unlettered_radio_button_preserves_identity():
    """
    Verifies that unlettered options are assigned original_label=None and
    never given invented letters in their stable representation.
    """
    text = (
        "What is the term for the computer software system in which organizations securely store, organize, query, and retrieve data?\n"
        "Database\n"
        "Cache\n"
        "Data ecosystem\n"
        "Catalog"
    )
    for ParserCls in [DesktopParser, BackendParser]:
        parser = ParserCls()
        result = parser.parse_from_text(text)
        
        assert result["has_original_labels"] is False
        for opt in result["structured_options"]:
            assert opt["original_label"] is None
            assert opt["id"].startswith("opt_")
            assert opt["source_order"] in [1, 2, 3, 4]
            assert opt["is_user_edited"] is False

        assert result["structured_options"][0]["text"] == "Database"
        assert result["structured_options"][0]["source_order"] == 1
        assert result["structured_options"][1]["text"] == "Cache"
        assert result["structured_options"][1]["source_order"] == 2
        assert result["structured_options"][2]["text"] == "Data ecosystem"
        assert result["structured_options"][2]["source_order"] == 3
        assert result["structured_options"][3]["text"] == "Catalog"
        assert result["structured_options"][3]["source_order"] == 4

# ---------------------------------------------------------------------------
# FIXTURE 5: OCR Artifacts such as 'c)' on Unlettered Options
# ---------------------------------------------------------------------------
def test_ocr_artifact_c_parenthesis_on_unlettered_options():
    """
    RapidOCR frequently outputs a radio circle '○' as 'c)' or 'C)'.
    If there are no preceding 'A)' or 'B)' options, this must NOT be treated
    as explicit letter mode.
    """
    text = (
        "Fill in the blank: During the planning phase, teams define goals.\n"
        "c) analyze\n"
        "planning\n"
        "capture\n"
        "manage"
    )
    for ParserCls in [DesktopParser, BackendParser]:
        parser = ParserCls()
        result = parser.parse_from_text(text)
        
        assert len(result["options"]) == 4
        # 'c)' is recognized as a radio circle or cleaned, preserving 4 options
        assert "analyze" in result["options"]["A"]
        assert result["options"]["B"] == "planning"
        assert result["options"]["C"] == "capture"
        assert result["options"]["D"] == "manage"

# ---------------------------------------------------------------------------
# FIXTURE 6: Variable Option Counts (2, 3, 4, 5, 6 options)
# ---------------------------------------------------------------------------
def test_variable_option_counts_2_to_6():
    # 2 options (Binary / True-False)
    tf_text = (
        "An operating system kernel runs in privileged supervisor mode.\n"
        "True\n"
        "False"
    )
    # 3 options (Coursera BTB)
    btb_text = (
        "1. Please check all answers that apply to Branch Target Buffer (BTB).\n"
        "The BTB allows the fetch stage of the pipeline to predict instruction addresses.\n"
        "The BTB is indexed by the current PC.\n"
        "The fetch stage with BTB needs to decode before predicting."
    )
    # 5 options (A-E)
    five_text = (
        "Identify the primary networking protocol:\n"
        "A) IP\n"
        "B) TCP\n"
        "C) UDP\n"
        "D) ICMP\n"
        "E) ARP"
    )
    # 6 options (A-F)
    six_text = (
        "Select Layer 4 protocols:\n"
        "A) TCP\n"
        "B) UDP\n"
        "C) SCTP\n"
        "D) DCCP\n"
        "E) SPX\n"
        "F) None of the above"
    )
    
    for ParserCls in [DesktopParser, BackendParser]:
        p = ParserCls()
        res_tf = p.parse_from_text(tf_text)
        assert len(res_tf["options"]) == 2
        assert res_tf["options"]["A"] == "True"
        assert res_tf["options"]["B"] == "False"
        
        res_btb = p.parse_from_text(btb_text)
        assert len(res_btb["options"]) == 3
        
        res_five = p.parse_from_text(five_text)
        assert len(res_five["options"]) == 5
        assert res_five["has_original_labels"] is True
        assert res_five["structured_options"][4]["original_label"] == "E"
        
        res_six = p.parse_from_text(six_text)
        assert len(res_six["options"]) == 6
        assert res_six["has_original_labels"] is True
        assert res_six["structured_options"][5]["original_label"] == "F"

# ---------------------------------------------------------------------------
# FIXTURE 7: Questions Containing Programming Instructions & Code
# ---------------------------------------------------------------------------
def test_programming_instructions_not_parsed_as_options():
    """
    Code lines containing assembly directives (LW, BEQZ, ADD, ADDI) must remain
    in the question statement and never be converted into options.
    """
    code_mcq = (
        "2. For Problems 2 through 8, consider the following MIPS assembly loop:\n"
        "loop:\n"
        "    LW   R1, 0(R2)\n"
        "    ANDI R4, R1, 1\n"
        "    BEQZ R4, skip\n"
        "    ADD  R5, R5, R1\n"
        "skip:\n"
        "    ADDI R2, R2, 4\n"
        "    SUBI R3, R3, 1\n"
        "    BNEZ R3, loop\n"
        "What does register R5 accumulate when the loop finishes?\n"
        "Sum of odd numbers in the array\n"
        "Sum of even numbers in the array\n"
        "Total count of array elements\n"
        "Memory base address pointer"
    )
    for ParserCls in [DesktopParser, BackendParser]:
        p = ParserCls()
        res = p.parse_from_text(code_mcq)
        q = res["question"]
        assert "LW   R1, 0(R2)" in q
        assert "BEQZ R4, skip" in q
        assert len(res["options"]) == 4
        assert res["options"]["A"] == "Sum of odd numbers in the array"
        assert res["options"]["B"] == "Sum of even numbers in the array"

# ---------------------------------------------------------------------------
# FIXTURE 8: Ambiguity Detection Workflow
# ---------------------------------------------------------------------------
def test_ambiguity_detection_duplicate_options():
    text = (
        "What is the capital of Japan?\n"
        "A) Tokyo\n"
        "B) Kyoto\n"
        "C) Tokyo\n"
        "D) Osaka"
    )
    for ParserCls in [DesktopParser, BackendParser]:
        p = ParserCls()
        res = p.parse_from_text(text)
        assert res["is_ambiguous"] is True
        assert len(res["duplicate_options"]) > 0
        assert any("Duplicate option text" in err for err in res["ambiguity_details"])

def test_ambiguity_detection_missing_blank():
    text = (
        "Fill in the blank: During the phase teams organize.\n"
        "A) plan\n"
        "B) capture\n"
        "C) manage\n"
        "D) analyze"
    )
    for ParserCls in [DesktopParser, BackendParser]:
        p = ParserCls()
        res = p.parse_from_text(text)
        assert res["is_ambiguous"] is True
        assert any("lacks a blank placeholder" in d for d in res["ambiguity_details"])

# ---------------------------------------------------------------------------
# FIXTURE 9: Curriculum Grounding Across All 6 Phases
# ---------------------------------------------------------------------------
def test_curriculum_grounding_all_six_phases():
    phases = {
        "Plan": (
            "During the initial phase, data teams determine what data is needed, establish project scope, and decide who will be responsible for it.",
            "Plan"
        ),
        "Capture": (
            "The data engineering group builds automated web ingest connectors to collect and acquire raw telemetry from external APIs.",
            "Capture"
        ),
        "Manage": (
            "A data team considers how and where data will be stored, what tools are required to safeguard it, and how to maintain it properly.",
            "Manage"
        ),
        "Analyze": (
            "Specialists clean and model the dataset, calculating correlation coefficients to extract actionable business insights.",
            "Analyze"
        ),
        "Archive": (
            "Ten-year-old financial ledgers are moved into encrypted cold storage for long-term retention and regulatory audit compliance.",
            "Archive"
        ),
        "Destroy": (
            "Following GDPR compliance mandates, customer records exceeding retention policies are permanently purged and shredded.",
            "Destroy"
        )
    }

    for phase_name, (scenario_text, expected_phase) in phases.items():
        for detect_fn in [desktop_detect_details, backend_detect_details]:
            details = detect_fn(scenario_text)
            assert details["subject"] == "Data Science", f"Expected Data Science for {phase_name}, got {details['subject']}"
            assert details["matched_phase"] == expected_phase, f"Expected {expected_phase}, got {details['matched_phase']}"
            assert details["curriculum_confidence"] >= 0.80
            assert details["evidence"] is not None
            assert "Google Data Analytics Standard" in details["evidence"]

# ---------------------------------------------------------------------------
# FIXTURE 10: Negative Grounding — Do NOT Force Data Science
# ---------------------------------------------------------------------------
def test_curriculum_grounding_does_not_force_data_science():
    # Math
    math_q = "Compute the integral of 4x^3 dx from 1 to 3."
    # Physics
    physics_q = "A projectile is launched with velocity v at an angle of 45 degrees. Calculate its kinetic energy."
    # General
    general_q = "What is the capital city of Canada?"

    for detect_fn in [desktop_detect_details, backend_detect_details]:
        res_m = detect_fn(math_q)
        assert res_m["subject"] == "Mathematics"
        assert res_m["curriculum_confidence"] == 0.0

        res_p = detect_fn(physics_q)
        assert res_p["subject"] == "Physics"
        assert res_p["curriculum_confidence"] == 0.0

        res_g = detect_fn(general_q)
        assert res_g["subject"] == "General"
        assert res_g["curriculum_confidence"] == 0.0

# ---------------------------------------------------------------------------
# FIXTURE 11: Cross-Architecture Equivalence (Desktop vs Backend)
# ---------------------------------------------------------------------------
def test_cross_architecture_parser_equivalence():
    sample_texts = [
        "What is the function of the ALU?\nA) Arithmetic calculations\nB) Cache indexing\nC) Instruction decode\nD) Branch prediction",
        "Fill in the blank: During the ___ phase, data teams decide what kind of data is needed.\nanalyze\nplanning\ncapture\nmanage",
        "Identify valid TCP flags:\nA) SYN\nB) ACK\nC) FIN\nD) RST\nE) PSH\nF) URG"
    ]
    desktop_p = DesktopParser()
    backend_p = BackendParser()

    for text in sample_texts:
        d_res = desktop_p.parse_from_text(text)
        b_res = backend_p.parse_from_text(text)

        assert d_res["question"] == b_res["question"]
        assert d_res["options"] == b_res["options"]
        assert d_res["has_original_labels"] == b_res["has_original_labels"]
        assert len(d_res["structured_options"]) == len(b_res["structured_options"])
        for i in range(len(d_res["structured_options"])):
            assert d_res["structured_options"][i] == b_res["structured_options"][i]

# ---------------------------------------------------------------------------
# FIXTURE 12: Copying Unlettered vs Lettered Answers
# ---------------------------------------------------------------------------
def format_copied_answer(original_label, answer_text, source_position, explanation):
    """Mirror exact copy logic in frontend/app/scanner/page.tsx"""
    header = (
        f"Correct Answer: Option {original_label}: {answer_text}"
        if original_label
        else f"Correct Answer: {answer_text} (Item #{source_position or 1})"
    )
    return f"{header}\n\nExplanation:\n{explanation}"

def test_copying_unlettered_answer():
    copied = format_copied_answer(
        original_label=None,
        answer_text="Database",
        source_position=2,
        explanation="A structured system used by organizations to securely store data."
    )
    assert copied.startswith("Correct Answer: Database (Item #2)")
    assert "Option" not in copied.splitlines()[0]
    assert "Explanation:\nA structured system" in copied

def test_copying_lettered_answer():
    copied = format_copied_answer(
        original_label="C",
        answer_text="Database",
        source_position=3,
        explanation="A structured system used by organizations to securely store data."
    )
    assert copied.startswith("Correct Answer: Option C: Database")
    assert "Explanation:\nA structured system" in copied

# ---------------------------------------------------------------------------
# FIXTURE 13: Preserving Option Identity After Manual Editing
# ---------------------------------------------------------------------------
def test_preserving_option_identity_after_manual_editing():
    text = (
        "What is the term for the computer software system in which organizations securely store data?\n"
        "Cache\n"
        "Datbase\n"
        "Catalog\n"
        "Data ecosystem"
    )
    parser = BackendParser()
    parsed = parser.parse_from_text(text)
    
    # Verify initial extracted options
    opts = parsed["structured_options"]
    assert len(opts) == 4
    target = opts[1] # "Datbase"
    assert target["id"] == "opt_2"
    assert target["source_order"] == 2
    assert target["original_label"] is None
    assert target["is_user_edited"] is False

    # Simulate student manual edit fixing typo in UI
    edited_opts = []
    for opt in opts:
        if opt["id"] == "opt_2":
            edited_opts.append({
                **opt,
                "text": "Database",
                "is_user_edited": True
            })
        else:
            edited_opts.append(dict(opt))

    # Verify identity, position, and label are preserved while text and flag update
    assert edited_opts[1]["id"] == "opt_2"
    assert edited_opts[1]["source_order"] == 2
    assert edited_opts[1]["original_label"] is None
    assert edited_opts[1]["internal_label"] == "B"
    assert edited_opts[1]["text"] == "Database"
    assert edited_opts[1]["is_user_edited"] is True

# ---------------------------------------------------------------------------
# FIXTURE 14: Preserving Option Identity Through API Request and Response
# ---------------------------------------------------------------------------
def test_preserving_option_identity_through_api_request_response():
    from unittest.mock import AsyncMock, patch
    from fastapi.testclient import TestClient
    from backend.app.main import app
    from backend.app.providers.base import QuestionAnalysisResult, ConfidenceModel, OptionIdentity

    client = TestClient(app)

    # Register/login test user
    email = "option_id_audit@exampilot.com"
    pwd = "AuditPassword123!"
    reg_res = client.post("/api/auth/register", json={"email": email, "password": pwd, "display_name": "Auditor"})
    if reg_res.status_code == 200:
        token = reg_res.json()["access_token"]
    else:
        login_res = client.post("/api/auth/login", json={"email": email, "password": pwd})
        token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    client.post("/api/providers", headers=headers, json={
        "provider": "openai",
        "api_key": "sk-proj-testkey1234567890abcdef1234",
        "default_model": "gpt-4o-mini",
        "is_default": True
    })

    # Mock provider generate_analysis to return structured answer
    mock_result = QuestionAnalysisResult(
        question="What is the term for the computer software system in which organizations store data?",
        suggested_answer="B",
        answer_text="Database",
        explanation="A database provides secure multi-user structured storage.",
        option_analysis={"A": "Incorrect", "B": "Correct", "C": "Incorrect", "D": "Incorrect"},
        confidence=ConfidenceModel(level="high", reason="Core computer systems standard"),
        subject="Computer Science"
    )

    req_payload = {
        "question_text": "What is the term for the computer software system in which organizations store data?",
        "options": {
            "A": "Cache",
            "B": "Database",
            "C": "Catalog",
            "D": "Data ecosystem"
        },
        "structured_options": [
            {"id": "opt_1", "text": "Cache", "original_label": None, "internal_label": "A", "source_order": 1, "confidence": 0.99, "is_user_edited": False},
            {"id": "opt_2", "text": "Database", "original_label": None, "internal_label": "B", "source_order": 2, "confidence": 0.98, "is_user_edited": True},
            {"id": "opt_3", "text": "Catalog", "original_label": None, "internal_label": "C", "source_order": 3, "confidence": 0.97, "is_user_edited": False},
            {"id": "opt_4", "text": "Data ecosystem", "original_label": None, "internal_label": "D", "source_order": 4, "confidence": 0.99, "is_user_edited": False}
        ],
        "subject": "Computer Science"
    }

    with patch("backend.app.providers.openai_provider.OpenAIProvider.generate_analysis", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = mock_result
        resp = client.post("/api/questions/analyse", headers=headers, json=req_payload)

    assert resp.status_code == 200, resp.text
    data = resp.json()

    # Verify unlettered identity: original_label is None, source_position is 2
    assert data["original_label"] is None
    assert data["source_position"] == 2
    assert data["answer_text"] == "Database"
    assert "structured_options" in data
    assert len(data["structured_options"]) == 4

    # Verify option 2 maintained is_user_edited=True and its identity
    opt2 = data["structured_options"][1]
    assert opt2["id"] == "opt_2"
    assert opt2["text"] == "Database"
    assert opt2["original_label"] is None
    assert opt2["source_order"] == 2
    assert opt2["is_user_edited"] is True

# ---------------------------------------------------------------------------
# FIXTURE 15: Correct Answer Display After Shuffled Option Sequence
# ---------------------------------------------------------------------------
def test_correct_answer_display_after_shuffled_option_sequence():
    """
    Online platforms randomize option orders between quiz attempts.
    Attempt 1: Database is Item #1.
    Attempt 2: Database is Item #3.
    Display must cleanly show Item #1 and Item #3 respectively without inventing letters.
    """
    attempt1_text = (
        "What is the term for the computer software system in which organizations securely store data?\n"
        "Database\n"
        "Data ecosystem\n"
        "Cache\n"
        "Catalog"
    )
    attempt2_text = (
        "What is the term for the computer software system in which organizations securely store data?\n"
        "Data ecosystem\n"
        "Cache\n"
        "Database\n"
        "Catalog"
    )
    p = BackendParser()
    res1 = p.parse_from_text(attempt1_text)
    res2 = p.parse_from_text(attempt2_text)

    # In Attempt 1, "Database" is source_order 1
    db_opt1 = next(o for o in res1["structured_options"] if o["text"] == "Database")
    assert db_opt1["source_order"] == 1
    assert db_opt1["original_label"] is None
    display1 = f"{db_opt1['text']} (Item #{db_opt1['source_order']})"
    assert display1 == "Database (Item #1)"

    # In Attempt 2, "Database" is source_order 3
    db_opt2 = next(o for o in res2["structured_options"] if o["text"] == "Database")
    assert db_opt2["source_order"] == 3
    assert db_opt2["original_label"] is None
    display2 = f"{db_opt2['text']} (Item #{db_opt2['source_order']})"
    assert display2 == "Database (Item #3)"

# ---------------------------------------------------------------------------
# FIXTURE 16: Backward Compatibility with Dictionary-Based Requests
# ---------------------------------------------------------------------------
def test_backward_compatibility_with_dictionary_based_requests():
    """
    Legacy clients sending only 'options': {'A': ..., 'B': ...} without structured_options
    must be fully supported without errors.
    """
    from unittest.mock import AsyncMock, patch
    from fastapi.testclient import TestClient
    from backend.app.main import app
    from backend.app.providers.base import QuestionAnalysisResult, ConfidenceModel

    client = TestClient(app)

    # Auth
    email = "legacy_compat@exampilot.com"
    pwd = "LegacyPassword123!"
    reg_res = client.post("/api/auth/register", json={"email": email, "password": pwd, "display_name": "Legacy Client"})
    token = reg_res.json()["access_token"] if reg_res.status_code == 200 else client.post("/api/auth/login", json={"email": email, "password": pwd}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/api/providers", headers=headers, json={
        "provider": "openai",
        "api_key": "sk-proj-testkey1234567890abcdef1234",
        "default_model": "gpt-4o-mini",
        "is_default": True
    })

    mock_result = QuestionAnalysisResult(
        question="Which transport protocol provides reliable byte-stream transmission?",
        suggested_answer="A",
        answer_text="TCP",
        explanation="TCP is connection-oriented and guarantees ordered delivery.",
        option_analysis={"A": "Correct: TCP is reliable", "B": "Incorrect: UDP is unreliable"},
        confidence=ConfidenceModel(level="high", reason="Networking standard"),
        subject="Networking"
    )

    legacy_payload = {
        "question_text": "Which transport protocol provides reliable byte-stream transmission?",
        "options": {
            "A": "TCP",
            "B": "UDP"
        },
        "subject": "Networking"
    }

    with patch("backend.app.providers.openai_provider.OpenAIProvider.generate_analysis", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = mock_result
        resp = client.post("/api/questions/analyse", headers=headers, json=legacy_payload)

    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["suggested_answer"] == "A"
    assert data["answer_text"] == "TCP"
    assert data["original_label"] == "A"
    assert data["source_position"] == 1
    assert "structured_options" in data
    assert len(data["structured_options"]) == 2
    assert data["structured_options"][0]["internal_label"] == "A"
    assert data["structured_options"][0]["text"] == "TCP"



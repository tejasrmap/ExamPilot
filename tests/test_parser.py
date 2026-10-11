"""
Unit Tests for ExamPilot Question Parser
GT InnoX LLP
"""

from desktop.core.question_parser import QuestionParser

def test_parse_standard_4_options():
    parser = QuestionParser()
    text = """
    Which data structure follows the First In First Out (FIFO) principle?
    A) Stack
    B) Queue
    C) Tree
    D) Graph
    """
    result = parser.parse_from_text(text)
    assert result["needs_correction"] is False
    assert "FIFO" in result["question"]
    assert len(result["options"]) == 4
    assert result["options"]["A"] == "Stack"
    assert result["options"]["B"] == "Queue"
    assert result["options"]["C"] == "Tree"
    assert result["options"]["D"] == "Graph"
    assert result["raw_text"] == text

def test_parse_5_options_numbered():
    parser = QuestionParser()
    text = """
    Q12. What is the value of limit as x approaches 0 of sin(x)/x?
    1. 0
    2. 1
    3. Infinity
    4. Undefined
    5. None of the above
    """
    result = parser.parse_from_text(text)
    assert result["needs_correction"] is False
    assert len(result["options"]) == 5
    assert result["options"]["A"] == "0"
    assert result["options"]["B"] == "1"
    assert result["options"]["E"] == "None of the above"

def test_parse_6_options_lettered():
    parser = QuestionParser()
    text = """
    Select all appropriate protocols operating at Layer 4:
    A) TCP
    B) UDP
    C) SCTP
    D) DCCP
    E) SPX
    F) None of the above
    """
    result = parser.parse_from_text(text)
    assert result["needs_correction"] is False
    assert len(result["options"]) == 6
    assert result["options"]["F"] == "None of the above"

def test_parse_math_symbols():
    parser = QuestionParser()
    text = """
    Evaluate the differential equation dy/dx = y * sqrt(x^2 + 1):
    A) y = C * e^(x^2/2)
    B) y = C * exp(integral(sqrt(x^2 + 1) dx))
    C) y = 0
    D) Undefined
    """
    result = parser.parse_from_text(text)
    assert result["needs_correction"] is False
    assert "sqrt(x^2 + 1)" in result["question"]
    assert len(result["options"]) == 4
    assert "exp(integral" in result["options"]["B"]

def test_parse_multiline_options():
    parser = QuestionParser()
    text = """
    Which statement about TCP flow control is accurate?
    A) The receiver advertises a receive window (rwnd)
       in every acknowledgment segment to prevent buffer overflow.
    B) The sender ignores receiver buffer capacity and
       relies solely on network packet loss timers.
    """
    result = parser.parse_from_text(text)
    assert result["needs_correction"] is False
    assert len(result["options"]) == 2
    assert "buffer overflow" in result["options"]["A"]
    assert "packet loss timers" in result["options"]["B"]

def test_parse_detect_missing_options():
    parser = QuestionParser()
    # Missing option C between B and D
    text = """
    Which protocol is connection-oriented?
    A) TCP
    B) UDP
    D) IP
    """
    result = parser.parse_from_text(text)
    assert result["needs_correction"] is True
    assert "C" in result["missing_options"]
    assert any("Missing intermediate option 'C'" in err for err in result["validation_issues"])

def test_parse_detect_duplicate_options():
    parser = QuestionParser()
    text = """
    What is the capital of France?
    A) Paris
    B) London
    C) Paris
    D) Rome
    """
    result = parser.parse_from_text(text)
    assert result["needs_correction"] is True
    assert len(result["duplicate_options"]) > 0
    assert any("Duplicate option text" in err for err in result["validation_issues"])

def test_parse_detect_incomplete_question():
    parser = QuestionParser()
    text = """
    What is
    A) Option 1
    B) Option 2
    """
    result = parser.parse_from_text(text)
    assert result["needs_correction"] is True
    assert any("incomplete" in err.lower() or "suspiciously short" in err.lower() for err in result["validation_issues"])

def test_parse_ambiguous_incomplete():
    parser = QuestionParser()
    text = "Just a stray sentence with no clear options."
    result = parser.parse_from_text(text)
    assert result["needs_correction"] is True

def test_parse_coursera_checkbox_question():
    parser = QuestionParser()
    text = """
    1. Please check all answers that apply to Branch Target Buffer (BTB).
    5 points
    [ ] The BTB allows the fetch stage of the pipeline to predict the address of the next instruction.
    [ ] The BTB is indexed by the current PC.
    [ ] The fetch stage with BTB needs to decode the instruction before predicting address.
    """
    result = parser.parse_from_text(text)
    assert result["needs_correction"] is False
    assert "Branch Target Buffer" in result["question"]
    assert len(result["options"]) == 3
    assert "pipeline to predict" in result["options"]["A"]
    assert "indexed by the current PC" in result["options"]["B"]
    assert "decode the instruction" in result["options"]["C"]

def test_parse_coursera_unlettered_lines():
    parser = QuestionParser()
    text = """
    1. Please check all answers that apply to Branch Target Buffer (BTB).
    The BTB allows the fetch stage of the pipeline to predict the address of the next instruction.
    The BTB is indexed by the current PC.
    The fetch stage with BTB needs to decode the instruction before predicting address.
    """
    result = parser.parse_from_text(text)
    assert result["needs_correction"] is False
    assert "Branch Target Buffer" in result["question"]
    assert len(result["options"]) == 3
    assert "pipeline to predict" in result["options"]["A"]
    assert "indexed by the current PC" in result["options"]["B"]
    assert "decode the instruction" in result["options"]["C"]

def test_parse_ocr_square_bullet_options():
    parser = QuestionParser()
    text = """
    1. Which cache mapping schemes are commonly used?
    口 Direct mapped
    口 Fully associative
    口 Set associative
    """
    result = parser.parse_from_text(text)
    assert result["needs_correction"] is False
    assert "cache mapping" in result["question"]
    assert len(result["options"]) == 3
    assert result["options"]["A"] == "Direct mapped"
    assert result["options"]["B"] == "Fully associative"
    assert result["options"]["C"] == "Set associative"

def test_parse_code_snippet_multiline_options():
    parser = QuestionParser()
    text = """
    2. For Problems 2 through 8, use the following Code Sequence: 3 points
    loop:
        LW   R1, 0(R2)
        ANDI R4, R1, 1
    b_1:
        BEQZ R4, 1_3
        ADD  R5, R5, R1
        J    1_4
    1_3:
        ADD  R6, R6, R1
    1_4:
        ADDI R2, R2, 4
        SUBI R3, R3, 1
    b_2:
        BNEZ R3, loop

    The above program sums the odd and even numbers in array and outputs them to two registers.
    Conceptually, what values are kept in R2 and R3? What do R5, and R6 contain when the loop exits?

    OR2 contains the loop iteration variable
    R3 contains the pointer that points to the different elements in the array
    R5 contains the sum of the odd numbers in the array
    R6 contains the sum of the even numbers in the array

    OR2 contains the loop iteration variable
    R3 contains the pointer that points to the different elements in the array
    R5 contains the sum of the even numbers in the array
    R6 contains the sum of the odd numbers in the array

    OR2 contains the pointer that points to the different elements in the array
    R3 contains the loop iteration variable
    R5 contains the sum of the even numbers in the array
    R6 contains the sum of the odd numbers in the array

    OR2 contains the pointer that points to the different elements in the array
    R3 contains the loop iteration variable
    R5 contains the sum of the odd numbers in the array
    R6 contains the sum of the even numbers in the array
    """
    result = parser.parse_from_text(text)
    assert result["needs_correction"] is False
    assert "Code Sequence" in result["question"]
    assert "loop:" in result["question"]
    assert "what values are kept in R2 and R3?" in result["question"]
    assert len(result["options"]) == 4
    assert "R2 contains the loop iteration variable" in result["options"]["A"]
    assert "R2 contains the pointer" in result["options"]["C"]

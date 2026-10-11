import re
from typing import Dict, Any, List, Optional

# Match metadata like "5 points", "1 point", "10 marks", "(3 pts)"
POINTS_PATTERN = re.compile(r"^\(?\d+\s*(?:points?|marks?|pts?)\)?$", re.IGNORECASE)

# Match question start like "1. ", "Q1: ", "Question 3 - "
QUESTION_PREFIX_PATTERN = re.compile(
    r"^(?:(?:Q|Question)\s*(?:\d{1,4})?\s*[\.\:\-\)]\s*|\d{1,4}\s*[\.\:\-\)]\s*)",
    re.IGNORECASE
)

# Standard letter options: A), (A), A., [A], A -, A:
OPTION_PATTERN = re.compile(
    r"^(?:(?:\(?([A-Ga-g]|(?:i|ii|iii|iv|v|vi))\s*(?:[\)\:\-\;\}]|\.(?!\d))\s*|\(([A-Ga-g]|(?:i|ii|iii|iv|v|vi))\)\s*|\[([A-Ga-g])\]\s*))(.*)$",
    re.IGNORECASE
)

# Numbered options: 1., (1), 1), [1] (handled carefully so not confused with question numbers)
NUM_OPTION_PATTERN = re.compile(
    r"^(?:(?:\(?(\d{1,2})\s*(?:[\)\:\-\;\}]|\.(?!\d))\s*|\((\d{1,2})\)\s*|\[(\d{1,2})\]\s*))(.*)$"
)

# Checkbox / bullet patterns: [ ], [x], 口, ☐, ☑, ( ), •, -, *
CHECKBOX_PATTERN = re.compile(
    r"^(?:\[[\s_xX✓✔\u2713\u2714]?\]|[\u53e3\u2610\u2611\u2612\u25a0-\u25a9\u25cb-\u25cf\u25ef\u2022\u2023\u25e6\u2219]|\([xX\s_✓✔*]?\)|\-\s+|\*\s+)\s*(.*)$"
)

INLINE_OPTION_SPLIT = re.compile(
    r"(?:(?<=\s)|(?<=^))(?:\(?([A-Ga-g]|\d{1,2})\s*(?:[\)\:\-\;]|\.(?!\d))\s*|\(([A-Ga-g]|\d{1,2})\)\s*|\[([A-Ga-g]|\d{1,2})\]\s*)"
)

def test_parse(text: str):
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    # Filter out metadata lines like "5 points"
    lines = [l for l in lines if not POINTS_PATTERN.match(l)]

    question_lines = []
    options = {}
    current_label = None
    current_text = []

    # Check if lines have letter options or checkboxes
    has_explicit_letters = any(OPTION_PATTERN.match(l) for l in lines)
    has_checkboxes = any(CHECKBOX_PATTERN.match(l) for l in lines)
    has_inline = any(len(list(INLINE_OPTION_SPLIT.finditer(l))) >= 2 for l in lines)

    next_auto_label = 'A'

    for idx, line in enumerate(lines):
        # 1. First line or before any question: if matches question prefix ("1. ...", "Q1: ...")
        if not question_lines and current_label is None and QUESTION_PREFIX_PATTERN.match(line):
            cleaned = QUESTION_PREFIX_PATTERN.sub("", line).strip()
            question_lines.append(cleaned)
            continue

        # 2. Checkbox / bullet matching
        cb_match = CHECKBOX_PATTERN.match(line)
        if cb_match:
            if current_label:
                options[current_label] = " ".join(current_text).strip()
                current_text = []
            current_label = next_auto_label
            next_auto_label = chr(ord(next_auto_label) + 1)
            content = cb_match.group(1).strip()
            if content:
                current_text.append(content)
            continue

        # 3. Explicit letter option: A), (A), A., [A]
        opt_match = OPTION_PATTERN.match(line)
        if opt_match:
            if current_label:
                options[current_label] = " ".join(current_text).strip()
                current_text = []
            lbl = (opt_match.group(1) or opt_match.group(2) or opt_match.group(3)).upper()
            current_label = lbl
            content = opt_match.group(4).strip()
            if content:
                current_text.append(content)
            continue

        # 4. Numbered option: 1., 2., 3. (only if question statement is already established)
        if len(question_lines) > 0:
            num_match = NUM_OPTION_PATTERN.match(line)
            if num_match:
                if current_label:
                    options[current_label] = " ".join(current_text).strip()
                    current_text = []
                num_val = int(num_match.group(1) or num_match.group(2) or num_match.group(3))
                # Map 1 -> A, 2 -> B, etc.
                if 1 <= num_val <= 8:
                    current_label = chr(ord('A') + num_val - 1)
                    content = num_match.group(4).strip()
                    if content:
                        current_text.append(content)
                    continue

        # 5. Un-lettered options fallback:
        # If question is established, and there are NO explicit letters/checkboxes anywhere in text,
        # each subsequent line is treated as an option
        if not has_explicit_letters and not has_checkboxes and not has_inline:
            if len(question_lines) > 0 and idx > 0:
                if current_label:
                    options[current_label] = " ".join(current_text).strip()
                    current_text = []
                current_label = next_auto_label
                next_auto_label = chr(ord(next_auto_label) + 1)
                current_text.append(line)
                continue

        # 6. Otherwise: if inside an option, continue option; else question
        if current_label is not None:
            current_text.append(line)
        else:
            question_lines.append(line)

    if current_label:
        options[current_label] = " ".join(current_text).strip()

    question_str = " ".join(question_lines).strip()
    return {"question": question_str, "options": options}

# Test 1: User's exact Coursera Question with checkboxes
c1 = """1. Please check all answers that apply to Branch Target Buffer (BTB).
5 points
[ ] The BTB allows the fetch stage of the pipeline to predict the address of the next instruction.
[ ] The BTB is indexed by the current PC.
[ ] The fetch stage with BTB needs to decode the instruction before predicting address."""

r1 = test_parse(c1)
print("TEST 1 (Coursera with [ ] and 5 points):")
print("Q:", r1["question"])
for k, v in r1["options"].items():
    print(f"  {k}: {v}")

# Test 2: User's Coursera Question without checkboxes (raw text lines)
c2 = """1. Please check all answers that apply to Branch Target Buffer (BTB).
5 points
The BTB allows the fetch stage of the pipeline to predict the address of the next instruction.
The BTB is indexed by the current PC.
The fetch stage with BTB needs to decode the instruction before predicting address."""

r2 = test_parse(c2)
print("\nTEST 2 (Coursera without [ ]):")
print("Q:", r2["question"])
for k, v in r2["options"].items():
    print(f"  {k}: {v}")

# Test 3: RapidOCR with \u53e3 (口)
c3 = """1. Please check all answers that apply to Branch Target Buffer (BTB).
口 The BTB allows the fetch stage of the pipeline to predict the address of the next instruction.
口 The BTB is indexed by the current PC.
口 The fetch stage with BTB needs to decode the instruction before predicting address."""

r3 = test_parse(c3)
print("\nTEST 3 (Coursera with OCR 口):")
print("Q:", r3["question"])
for k, v in r3["options"].items():
    print(f"  {k}: {v}")

# Test 4: Standard A, B, C, D
c4 = """What is 5 * 5?
A) 20
B) 25
C) 30
D) 35"""

r4 = test_parse(c4)
print("\nTEST 4 (Standard A-D):")
print("Q:", r4["question"])
for k, v in r4["options"].items():
    print(f"  {k}: {v}")

# Test 5: Numbered options 1., 2., 3., 4.
c5 = """Q2: Which protocol provides reliable transmission?
1. UDP
2. TCP
3. ICMP
4. IP"""

r5 = test_parse(c5)
print("\nTEST 5 (Numbered 1-4):")
print("Q:", r5["question"])
for k, v in r5["options"].items():
    print(f"  {k}: {v}")


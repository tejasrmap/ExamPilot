import re
from typing import Dict, Any, List, Optional

POINTS_PATTERN = re.compile(r"^\(?\d+\s*(?:points?|marks?|pts?)\)?$", re.IGNORECASE)

QUESTION_PREFIX_PATTERN = re.compile(
    r"^(?:(?:Q|Question)\s*(?:\d{1,4})?\s*[\.\:\-\)]\s*|\d{1,4}\s*[\.\:\-\)]\s*)",
    re.IGNORECASE
)

OPTION_PATTERN = re.compile(
    r"^(?:(?:\(?([A-Ga-g]|(?:i|ii|iii|iv|v|vi))\s*(?:[\)\:\-\;\}]|\.(?!\d))\s*|\(([A-Ga-g]|(?:i|ii|iii|iv|v|vi))\)\s*|\[([A-Ga-g])\]\s*))(.*)$",
    re.IGNORECASE
)

NUM_OPTION_PATTERN = re.compile(
    r"^(?:(?:\(?(\d{1,2})\s*(?:[\)\:\-\;\}]|\.(?!\d))\s*|\((\d{1,2})\)\s*|\[(\d{1,2})\]\s*))(.*)$"
)

# Robust radio and checkbox detection:
# Matches:
# 1. Standard markdown / OCR checkboxes: [ ], [x], 口, ☐, ☑, ☒, ( ), (*), ○, ●, •
# 2. OCR radio button circle recognized as O or o at line start:
#    - Standalone "O " or "o " (followed by space or punctuation)
#    - "O" attached to word at line start where "O" is a circle radio glyph (e.g. "OR2", "OThe", "OOption")
CHECKBOX_PATTERN = re.compile(
    r"^(?:\[[\s_xX✓✔\u2713\u2714]?\]|[\u53e3\u2610\u2611\u2612\u25a0-\u25a9\u25cb-\u25cf\u25ef\u2022\u2023\u25e6\u2219]|\([xX\s_✓✔*]?\)|\b[oO]\b|[oO](?=[A-Za-z0-9])|\-\s+|\*\s+)\s*(.*)$"
)

INLINE_OPTION_SPLIT = re.compile(
    r"(?:(?<=\s)|(?<=^))(?:\(?([A-Ga-g]|\d{1,2})\s*(?:[\)\:\-\;]|\.(?!\d))\s*|\(([A-Ga-g]|\d{1,2})\)\s*|\[([A-Ga-g]|\d{1,2})\]\s*)"
)

def parse_full(text: str):
    raw_lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    lines = [l for l in raw_lines if not POINTS_PATTERN.match(l)]

    question_lines: List[str] = []
    options: Dict[str, str] = {}
    current_label: Optional[str] = None
    current_text: List[str] = []

    has_explicit_letters = any(OPTION_PATTERN.match(l) for l in lines)
    has_checkboxes = any(CHECKBOX_PATTERN.match(l) for l in lines)
    has_inline = any(len(list(INLINE_OPTION_SPLIT.finditer(l))) >= 2 for l in lines)

    next_auto_label = 'A'

    # If no explicit markers or checkboxes, find where the question prompt ends (last '?')
    question_end_idx = -1
    if not has_explicit_letters and not has_checkboxes and not has_inline:
        for i, l in enumerate(lines):
            if "?" in l:
                question_end_idx = i

    for idx, line in enumerate(lines):
        # 1. Inline options check
        inline_matches = list(INLINE_OPTION_SPLIT.finditer(line))
        if len(inline_matches) >= 2:
            if not question_lines and inline_matches[0].start() > 0:
                q_p = line[:inline_matches[0].start()].strip()
                if q_p:
                    question_lines.append(q_p)
            if current_label:
                options[current_label] = " ".join(current_text).strip()
                current_text = []
                current_label = None
            for i, m in enumerate(inline_matches):
                lbl = (m.group(1) or m.group(2) or m.group(3) or "").upper()
                s = m.end()
                e = inline_matches[i+1].start() if i+1 < len(inline_matches) else len(line)
                options[lbl] = line[s:e].strip()
            continue

        # 2. Before any options have been found, if line matches question prefix e.g. "1. ", "2. ", "Q1: "
        if not question_lines and current_label is None and QUESTION_PREFIX_PATTERN.match(line):
            cleaned = QUESTION_PREFIX_PATTERN.sub("", line).strip()
            if cleaned:
                question_lines.append(cleaned)
            continue

        # 3. Checkbox / Radio button match (e.g. [ ], 口, ( ), OR2, O...)
        cb_match = CHECKBOX_PATTERN.match(line)
        if cb_match:
            if current_label:
                options[current_label] = " ".join(current_text).strip()
                current_text = []

            current_label = next_auto_label
            next_auto_label = chr(ord(next_auto_label) + 1)
            opt_c = cb_match.group(1).strip()
            if opt_c:
                current_text.append(opt_c)
            continue

        # 4. Explicit letter option: A), (A), A.
        opt_match = OPTION_PATTERN.match(line)
        if opt_match:
            if current_label:
                options[current_label] = " ".join(current_text).strip()
                current_text = []
            lbl = (opt_match.group(1) or opt_match.group(2) or opt_match.group(3)).upper()
            current_label = lbl
            opt_c = opt_match.group(4).strip()
            if opt_c:
                current_text.append(opt_c)
            continue

        # 5. Numbered options (1., 2., 3., 4.) after question is identified
        if len(question_lines) > 0:
            num_match = NUM_OPTION_PATTERN.match(line)
            if num_match:
                if current_label:
                    options[current_label] = " ".join(current_text).strip()
                    current_text = []
                num_v = int(num_match.group(1) or num_match.group(2) or num_match.group(3))
                if 1 <= num_v <= 8:
                    current_label = chr(ord('A') + num_v - 1)
                    opt_c = num_match.group(4).strip()
                    if opt_c:
                        current_text.append(opt_c)
                    continue

        # 6. Un-lettered options fallback:
        # ONLY apply if there are NO explicit letters/checkboxes anywhere,
        # AND we are past the question prompt (or question prompt was established)
        if not has_explicit_letters and not has_checkboxes and not has_inline:
            # Check if this line is an option:
            # If question prompt ended at question_end_idx, lines after question_end_idx are options
            remaining_lines_count = len(lines) - 1 - (question_end_idx if question_end_idx >= 0 else 0)
            if 2 <= remaining_lines_count <= 8:
                if question_end_idx >= 0 and idx > question_end_idx:
                    if current_label:
                        options[current_label] = " ".join(current_text).strip()
                        current_text = []
                    current_label = next_auto_label
                    next_auto_label = chr(ord(next_auto_label) + 1)
                    current_text.append(line)
                    continue
                elif question_end_idx < 0 and len(question_lines) > 0 and idx > 0:
                    if current_label:
                        options[current_label] = " ".join(current_text).strip()
                        current_text = []
                    current_label = next_auto_label
                    next_auto_label = chr(ord(next_auto_label) + 1)
                    current_text.append(line)
                    continue

        # 7. Continuation:
        if current_label is not None:
            current_text.append(line)
        else:
            question_lines.append(line)

    if current_label:
        options[current_label] = " ".join(current_text).strip()

    q_str = " ".join(question_lines).strip()
    return {"question": q_str, "options": options}

# Test Question 2:
q2_text = """2. For Problems 2 through 8, use the following Code Sequence: 3 points
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
R6 contains the sum of the even numbers in the array"""

res = parse_full(q2_text)
print("QUESTION 2 PARSED:")
print("Question text (first 100 chars):", res["question"][:100], "...")
print("Question text (last 100 chars): ...", res["question"][-100:])
print(f"Total options: {len(res['options'])}")
for k, v in res["options"].items():
    print(f"  Option {k}: {v[:80]}...")


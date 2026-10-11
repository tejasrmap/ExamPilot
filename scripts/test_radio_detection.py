import re

# Test lines exactly as extracted from Coursera Question 2:
lines = [
    "2. For Problems 2 through 8, use the following Code Sequence: 3 points",
    "loop:",
    "LW R1, 0(R2)",
    "ANDI R4, R1, 1",
    "b_1:",
    "BEQZ R4, 1_3",
    "ADD R5, R5, R1",
    "J 1_4",
    "1_3:",
    "ADD R6, R6, R1",
    "1_4:",
    "ADDI R2, R2, 4",
    "SUBI R3, R3, 1",
    "b_2:",
    "BNEZ R3, loop",
    "The above program sums the odd and even numbers in array and outputs them to two registers.",
    "Conceptually, what values are kept in R2 and R3? What do R5, and R6 contain when the loop exits?",
    "OR2 contains the loop iteration variable",
    "R3 contains the pointer that points to the different elements in the array",
    "R5 contains the sum of the odd numbers in the array",
    "R6 contains the sum of the even numbers in the array",
    "OR2 contains the loop iteration variable",
    "R3 contains the pointer that points to the different elements in the array",
    "R5 contains the sum of the even numbers in the array",
    "R6 contains the sum of the odd numbers in the array",
    "OR2 contains the pointer that points to the different elements in the array",
    "R3 contains the loop iteration variable",
    "R5 contains the sum of the even numbers in the array",
    "R6 contains the sum of the odd numbers in the array",
    "OR2 contains the pointer that points to the different elements in the array",
    "R3 contains the loop iteration variable",
    "R5 contains the sum of the odd numbers in the array",
    "R6 contains the sum of the even numbers in the array"
]

# Radio / checkbox pattern:
# Recognizes:
# 1. Standard markdown / unicode checkboxes: [ ], [x], 口, ☐, ☑, ( ), (*), ○, ●, •
# 2. OCR radio button circle recognized as O or o at line start:
#    - Standalone "O " or "o "
#    - "O" attached to word at line start where "O" is a circle radio glyph (e.g. "OR2", "OThe", "OOption")
CHECKBOX_PATTERN = re.compile(
    r"^(?:\[[\s_xX✓✔\u2713\u2714]?\]|[\u53e3\u2610\u2611\u2612\u25a0-\u25a9\u25cb-\u25cf\u25ef\u2022\u2023\u25e6\u2219]|\([xX\s_✓✔*]?\)|\b[oO]\b|[oO](?=[A-Za-z0-9])|\-\s+|\*\s+)\s*(.*)$"
)

QUESTION_PREFIX_PATTERN = re.compile(
    r"^(?:(?:Q|Question)\s*(?:\d{1,4})?\s*[\.\:\-\)]\s*|\d{1,4}\s*[\.\:\-\)]\s*)",
    re.IGNORECASE
)

POINTS_PATTERN = re.compile(r"^\(?\d+\s*(?:points?|marks?|pts?)\)?$", re.IGNORECASE)

# Let's test matching each line:
print("Checkbox matches:")
for idx, l in enumerate(lines):
    m = CHECKBOX_PATTERN.match(l)
    if m:
        print(f"Line {idx} matches radio/checkbox: stripped content = '{m.group(1)}'")


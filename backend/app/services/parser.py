"""
ExamPilot MCQ Question Parser Module
Converts raw OCR text lines or raw text into structured question + options.
Supports varying option counts (A-E, A-F, 2-6 options), mathematical notations,
gap detection (missing options), duplicate option detection, and ambiguity flagging.
GT InnoX LLP
"""

import re
from typing import Dict, Any, List, Optional, Tuple, Set
from desktop.utils.logger import logger

class QuestionParser:
    """Robust parser for extracting structured MCQ questions and options."""

    # Metadata pattern to ignore lines like "5 points", "1 point", "10 marks", "(2 pts)"
    POINTS_PATTERN = re.compile(r"^\(?\d+\s*(?:points?|marks?|pts?)\)?$", re.IGNORECASE)

    # Assembly / code label and instruction pattern to prevent code lines from turning into options
    CODE_INSTRUCTION_PATTERN = re.compile(
        r"^(?:[a-zA-Z_][a-zA-Z0-9_]*\s*:\s*$|(?:LW|SW|ADD|ADDI|SUB|SUBI|AND|ANDI|OR|ORI|XOR|XORI|BEQ|BNE|BEQZ|BNEZ|J|JAL|JR|MOV|PUSH|POP|CMP|NOP|INT|RET|CALL)\b)",
        re.IGNORECASE
    )

    # Question prefix at the start of a problem (e.g. "1. ", "Q1: ", "Question 3 - ")
    QUESTION_PREFIX_PATTERN = re.compile(
        r"^(?:(?:Q|Question)\s*(?:\d{1,4})?\s*[\.\:\-\)]\s*|\d{1,4}\s*[\.\:\-\)]\s*)",
        re.IGNORECASE
    )

    # Instruction prefix headers (e.g. "Fill in the blank:", "Consider the following:")
    INSTRUCTION_PREFIX = re.compile(
        r"^(?:(?:\d+[\.\)]\s*)?(?:fill\s+in\s+the\s+blanks?|consider\s+the\s+following|answer\s+the\s+following|for\s+questions?\s*\d+|select\s+the\s+best\s+answer|read\s+the\s+following|choose\s+the\s+correct\s+option)[\:\.]?)$",
        re.IGNORECASE
    )

    DANGLING_WORDS = {
        "the", "a", "an", "of", "to", "in", "for", "with", "on", "at", "from",
        "by", "about", "as", "into", "like", "through", "after", "over", "between",
        "out", "against", "during", "without", "before", "under", "around", "among",
        "and", "or", "but", "nor", "so", "yet", "is", "are", "was", "were", "be",
        "been", "being", "have", "has", "had", "do", "does", "did", "will", "would",
        "shall", "should", "may", "might", "must", "can", "could", "who", "which",
        "that", "whose", "whom", "where", "when"
    }

    # Standard letter/roman option prefixes: "A)", "(A)", "A.", "[A]", "A -", "A: ", "i.", "(i)"
    OPTION_PATTERN = re.compile(
        r"^(?:(?:\(?([A-Ga-g]|(?:i|ii|iii|iv|v|vi))\s*(?:[\)\:\-\;\}]|\.(?!\d))\s*|\(([A-Ga-g]|(?:i|ii|iii|iv|v|vi))\)\s*|\[([A-Ga-g])\]\s*))(.*)$",
        re.IGNORECASE
    )

    # Numbered options: "1.", "2.", "3.", "(1)", "1)" (handled after question statement is identified)
    NUM_OPTION_PATTERN = re.compile(
        r"^(?:(?:\(?(\d{1,2})\s*(?:[\)\:\-\;\}]|\.(?!\d))\s*|\((\d{1,2})\)\s*|\[(\d{1,2})\]\s*))(.*)$"
    )

    # Checkbox and bullet indicators: [ ], [x], 口, ☐, ☑, ☒, □, ○, ●, ( ), (*), •, -, *
    # Includes OCR radio circle detection: standalone 'O ' or 'O' prepended to letters (e.g. 'OR2', 'OThe'), fullwidth parentheses
    CHECKBOX_PATTERN = re.compile(
        r"^(?:\[[\s_xX✓✔\u2713\u2714]?\]|[\u53e3\u2610\u2611\u2612\u25a0-\u25a9\u25cb-\u25cf\u25ef\u2022\u2023\u25e6\u2219]|\([xX\s_✓✔*]?\)|\uff08[xX\s_✓✔*]?\uff09|\b[oO]\b|[oO](?=[A-Za-z0-9])|\-\s+|\*\s+)\s*(.*)$"
    )

    # Inline options pattern when multiple options exist on the same line: "A) First  B) Second"
    INLINE_OPTION_SPLIT = re.compile(
        r"(?:(?<=\s)|(?<=^))(?:\(?([A-Ga-g]|\d{1,2})\s*(?:[\)\:\-\;]|\.(?!\d))\s*|\(([A-Ga-g]|\d{1,2})\)\s*|\[([A-Ga-g]|\d{1,2})\]\s*)"
    )

    ROMAN_MAP = {"i": "A", "ii": "B", "iii": "C", "iv": "D", "v": "E", "vi": "F"}
    NUM_MAP = {"1": "A", "2": "B", "3": "C", "4": "D", "5": "E", "6": "F", "7": "G", "8": "H"}

    def parse_from_lines(self, lines: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parse structured MCQ data from OCR line items preserving line-level confidence.
        Each item has 'text' and 'confidence'.
        """
        raw_strings = [item["text"] for item in lines if item.get("text")]
        combined_text = "\n".join(raw_strings)
        parsed = self.parse_from_text(combined_text, lines_metadata=lines)

        # Average confidence from OCR lines
        scores = [item["confidence"] for item in lines if "confidence" in item and item["confidence"] is not None]
        if scores:
            parsed["confidence"] = round(sum(scores) / len(scores), 3)

        return parsed

    def _normalize_label(self, raw_label: str) -> str:
        """Map numbers (1,2,3) and roman numerals (i,ii) to uppercase letters (A,B,C)."""
        clean = raw_label.strip().lower()
        if clean in self.ROMAN_MAP:
            return self.ROMAN_MAP[clean]
        if clean in self.NUM_MAP:
            return self.NUM_MAP[clean]
        return clean.upper()

    def _find_question_end(self, lines: List[str]) -> int:
        """
        Determines the 0-based line index where the question statement ends.
        Lines strictly after this index are candidate options.
        """
        if len(lines) <= 2:
            return 0

        # 1. Look for explicit question mark '?' where 2 to 6 candidate option lines remain
        for i in range(len(lines) - 1, -1, -1):
            if "?" in lines[i]:
                rem = len(lines) - 1 - i
                if 2 <= rem <= 6:
                    return i
                # Check for an instruction line right after '?' e.g. "Select one:"
                if i + 1 < len(lines) and lines[i + 1].rstrip().endswith(":"):
                    rem2 = len(lines) - 1 - (i + 1)
                    if 2 <= rem2 <= 6:
                        return i + 1

        # 2. Look for fill-in-the-blank placeholders ('_____', '___')
        blank_indices = [i for i, l in enumerate(lines) if re.search(r"_{2,}", l)]
        actual_blanks = [i for i in blank_indices if not self.INSTRUCTION_PREFIX.match(lines[i])]
        if actual_blanks:
            for i in range(actual_blanks[0], len(lines)):
                if lines[i].rstrip().endswith("."):
                    rem = len(lines) - 1 - i
                    if 2 <= rem <= 6:
                        return i

        # 2b. If line 0 is a standalone question prefix with complete sentence ending in '.' or ':'
        if self.QUESTION_PREFIX_PATTERN.match(lines[0]) and lines[0].rstrip().endswith((".", ":")):
            if not self.INSTRUCTION_PREFIX.match(lines[0]) and not re.search(r"_{2,}", lines[0]):
                rem = len(lines) - 1
                if 2 <= rem <= 8:
                    return 0

        # 3. Look for the last line ending with a period '.' or colon ':' where remaining lines (2 to 6) are options
        for i in range(len(lines) - 3, -1, -1):
            if lines[i].rstrip().endswith((".", ":")):
                if not self.INSTRUCTION_PREFIX.match(lines[i]):
                    rem = len(lines) - 1 - i
                    if 2 <= rem <= 6:
                        return i

        # 4. Fallback: Check candidate option counts: prefer 4 (standard MCQ), then 3, 5, 2
        for opt_count in (4, 3, 5, 2):
            if len(lines) > opt_count:
                cand_end = len(lines) - opt_count - 1
                if self.INSTRUCTION_PREFIX.match(lines[cand_end]):
                    continue
                return cand_end

        return 0

    def parse_from_text(self, text: str, lines_metadata: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Parse unstructured text into structured MCQ with stable option identity and comprehensive validation.
        Option representation preserves:
          - id (e.g. opt_1)
          - text
          - original_label (None if unlettered radio buttons, 'A'/'B' if visible)
          - internal_label (internal key for downstream model queries)
          - source_order (1, 2, 3...)
          - confidence (OCR confidence if available)
          - is_user_edited (False by default)
        """
        if not text or not text.strip():
            return {
                "question": "",
                "options": {},
                "structured_options": [],
                "has_original_labels": False,
                "raw_text": "",
                "confidence": 0.0,
                "needs_correction": True,
                "is_ambiguous": True,
                "ambiguity_details": ["No text provided to parse."],
                "missing_options": [],
                "duplicate_options": [],
                "validation_issues": ["No text provided to parse."],
                "error": "No text provided to parse."
            }

        cleaned_text = text.strip()
        raw_lines = [line.strip() for line in cleaned_text.splitlines() if line.strip()]

        # Filter out standalone point badges e.g. "5 points"
        lines = [l for l in raw_lines if not self.POINTS_PATTERN.match(l)]

        question_lines: List[str] = []
        
        # Intermediate tracking for option records
        options_records: List[Dict[str, Any]] = []
        current_option_idx: Optional[int] = None

        explicit_matches = [self.OPTION_PATTERN.match(l) for l in lines if self.OPTION_PATTERN.match(l)]
        found_labels = [
            (m.group(1) or m.group(2) or m.group(3) or "").strip().upper()
            for m in explicit_matches
        ]
        has_explicit_letters = ('A' in found_labels) or len(set(found_labels)) >= 2
        has_checkboxes = any(self.CHECKBOX_PATTERN.match(l) for l in lines)
        has_inline = any(len(list(self.INLINE_OPTION_SPLIT.finditer(l))) >= 2 for l in lines)
        next_auto_label = 'A'

        # If no explicit markers or checkboxes, find where the question prompt ends
        question_end_idx = -1
        if not has_explicit_letters and not has_checkboxes and not has_inline:
            question_end_idx = self._find_question_end(lines)

        for idx, line in enumerate(lines):
            # Check for inline horizontal options (e.g. "A) Red   B) Green   C) Blue")
            inline_matches = list(self.INLINE_OPTION_SPLIT.finditer(line))
            if len(inline_matches) >= 2:
                if not question_lines and inline_matches[0].start() > 0:
                    q_prefix = line[:inline_matches[0].start()].strip()
                    if q_prefix:
                        question_lines.append(q_prefix)

                current_option_idx = None

                for i, m in enumerate(inline_matches):
                    lbl_raw = m.group(1) or m.group(2) or m.group(3) or ""
                    clean_orig = re.sub(r"[\(\)\[\]\:\-\.\s]", "", lbl_raw).strip()
                    norm_lbl = self._normalize_label(clean_orig)
                    start_pos = m.end()
                    end_pos = inline_matches[i+1].start() if i + 1 < len(inline_matches) else len(line)
                    val = line[start_pos:end_pos].strip()
                    
                    options_records.append({
                        "internal_label": norm_lbl,
                        "original_label": clean_orig.upper(),
                        "source_order": len(options_records) + 1,
                        "text_parts": [val] if val else [],
                        "line_indices": [idx]
                    })
                continue

            # 1. First line / prior to question statement:
            if not question_lines and current_option_idx is None and self.QUESTION_PREFIX_PATTERN.match(line):
                cleaned_q = self.QUESTION_PREFIX_PATTERN.sub("", line).strip()
                if cleaned_q:
                    question_lines.append(cleaned_q)
                continue

            # 1b. Assembly code / label check
            if self.CODE_INSTRUCTION_PATTERN.match(line):
                if current_option_idx is not None:
                    options_records[current_option_idx]["text_parts"].append(line)
                    options_records[current_option_idx]["line_indices"].append(idx)
                else:
                    question_lines.append(line)
                continue

            # 2. Explicit letter option prefix (A., A), (A), [A]) - checked before checkboxes
            if has_explicit_letters:
                letter_match = self.OPTION_PATTERN.match(line)
                if letter_match:
                    raw_lbl = letter_match.group(1) or letter_match.group(2) or letter_match.group(3) or ""
                    clean_orig = re.sub(r"[\(\)\[\]\:\-\.\s]", "", raw_lbl).strip()
                    norm_lbl = self._normalize_label(clean_orig)
                    opt_content = letter_match.group(4).strip()
                    
                    options_records.append({
                        "internal_label": norm_lbl,
                        "original_label": clean_orig.upper(),
                        "source_order": len(options_records) + 1,
                        "text_parts": [opt_content] if opt_content else [],
                        "line_indices": [idx]
                    })
                    current_option_idx = len(options_records) - 1
                    continue

            # 3. Checkbox / bullet option matching e.g. [ ], [x], 口, •, -
            cb_match = self.CHECKBOX_PATTERN.match(line)
            if cb_match:
                norm_lbl = next_auto_label
                next_auto_label = chr(ord(next_auto_label) + 1)
                opt_content = cb_match.group(1).strip()

                options_records.append({
                    "internal_label": norm_lbl,
                    "original_label": None,  # Checkboxes are unlettered: never invent option letters
                    "source_order": len(options_records) + 1,
                    "text_parts": [opt_content] if opt_content else [],
                    "line_indices": [idx]
                })
                current_option_idx = len(options_records) - 1
                continue

            # 4. Numbered option (1., 2., 3., 4.) when question statement already exists
            if len(question_lines) > 0:
                num_match = self.NUM_OPTION_PATTERN.match(line)
                if num_match:
                    raw_num = num_match.group(1) or num_match.group(2) or num_match.group(3) or ""
                    clean_orig = raw_num.strip()
                    norm_lbl = self._normalize_label(clean_orig)
                    opt_content = num_match.group(4).strip()

                    options_records.append({
                        "internal_label": norm_lbl,
                        "original_label": clean_orig,
                        "source_order": len(options_records) + 1,
                        "text_parts": [opt_content] if opt_content else [],
                        "line_indices": [idx]
                    })
                    current_option_idx = len(options_records) - 1
                    continue

            # 5. Un-lettered option fallback:
            if not has_explicit_letters and not has_checkboxes and not has_inline:
                if question_end_idx >= 0:
                    if idx <= question_end_idx:
                        question_lines.append(line)
                        continue
                    else:
                        norm_lbl = next_auto_label
                        next_auto_label = chr(ord(next_auto_label) + 1)

                        options_records.append({
                            "internal_label": norm_lbl,
                            "original_label": None,  # Unlettered options: never invent option letters
                            "source_order": len(options_records) + 1,
                            "text_parts": [line],
                            "line_indices": [idx]
                        })
                        current_option_idx = len(options_records) - 1
                        continue

            # 6. Continuation line:
            if current_option_idx is not None:
                options_records[current_option_idx]["text_parts"].append(line)
                options_records[current_option_idx]["line_indices"].append(idx)
            else:
                question_lines.append(line)

        # Build structured options with identity
        structured_options: List[Dict[str, Any]] = []
        options_dict: Dict[str, str] = {}

        for rec in options_records:
            opt_text = " ".join(rec["text_parts"]).strip()
            opt_conf = None
            if lines_metadata:
                matched_scores = []
                for line_i in rec["line_indices"]:
                    if 0 <= line_i < len(lines_metadata) and "confidence" in lines_metadata[line_i]:
                        c_val = lines_metadata[line_i]["confidence"]
                        if c_val is not None:
                            matched_scores.append(float(c_val))
                if matched_scores:
                    opt_conf = round(sum(matched_scores) / len(matched_scores), 3)

            opt_obj = {
                "id": f"opt_{rec['source_order']}",
                "text": opt_text,
                "original_label": rec["original_label"],
                "internal_label": rec["internal_label"],
                "source_order": rec["source_order"],
                "confidence": opt_conf,
                "is_user_edited": False
            }
            structured_options.append(opt_obj)
            options_dict[rec["internal_label"]] = opt_text

        has_original_labels = any(opt["original_label"] is not None for opt in structured_options)

        # Combine question text and strip standard question prefixes like "Q1: ", "1. "
        question_str = " ".join(question_lines).strip()
        question_str = self.QUESTION_PREFIX_PATTERN.sub("", question_str).strip()

        # Validation Checks & Ambiguity Detection
        validation_issues: List[str] = []
        missing_options: List[str] = []
        duplicate_options: List[str] = []
        ambiguity_details: List[str] = []

        # 1. Incomplete Question check
        if not question_str or len(question_str) < 5:
            issue = "Question statement is missing or suspiciously short (< 5 characters)."
            validation_issues.append(issue)
            ambiguity_details.append(issue)
        elif len(question_str) < 15 and not any(c in question_str for c in ["?", ":", "="]):
            issue = "Question statement may be incomplete."
            validation_issues.append(issue)
            ambiguity_details.append(issue)

        # 1b. Missing placeholder check in fill-in-the-blank questions
        clean_prompt = re.sub(r"\bfill\s+in\s+the\s+blanks?[\:\.]?\s*", "", question_str, flags=re.IGNORECASE).strip()
        if re.search(r"\bfill\s+in\s+the\s+blanks?\b", question_str, re.IGNORECASE) and not re.search(r"_{2,}|\[blank\]|\bblank\b|\.{3,}", clean_prompt, re.IGNORECASE):
            issue = "Fill-in-the-blank prompt lacks a blank placeholder (___)."
            validation_issues.append(issue)
            ambiguity_details.append(issue)

        # 2. Options count check
        if len(structured_options) < 2:
            issue = f"Insufficient options detected ({len(structured_options)} found). Multiple choice requires at least 2."
            validation_issues.append(issue)
            ambiguity_details.append(issue)

        # 3. Gap / Missing options check (only applicable if original letters were present)
        if has_original_labels:
            sorted_keys = sorted(options_dict.keys())
            if sorted_keys and all(len(k) == 1 and k.isalpha() for k in sorted_keys):
                last_ord = ord(sorted_keys[-1].upper())
                full_expected = [chr(c) for c in range(ord('A'), last_ord + 1)]
                for exp in full_expected:
                    if exp not in options_dict and exp < sorted_keys[-1].upper():
                        missing_options.append(exp)
                        issue = f"Missing intermediate option '{exp}' detected."
                        validation_issues.append(issue)
                        ambiguity_details.append(issue)

        # 4. Duplicate option values check
        seen_values: Dict[str, str] = {}
        for opt_key, opt_val in options_dict.items():
            norm_val = re.sub(r"\s+", " ", opt_val.strip().lower())
            if norm_val:
                if norm_val in seen_values:
                    dup_pair = f"{seen_values[norm_val]} & {opt_key}"
                    duplicate_options.append(dup_pair)
                    issue = f"Duplicate option text found between {dup_pair} ('{opt_val}')."
                    validation_issues.append(issue)
                    ambiguity_details.append(issue)
                else:
                    seen_values[norm_val] = opt_key

        # 5. Empty option content check
        for opt_key, opt_val in list(options_dict.items()):
            if not opt_val.strip():
                issue = f"Option '{opt_key}' has empty text."
                validation_issues.append(issue)
                ambiguity_details.append(issue)

        is_ambiguous = len(ambiguity_details) > 0
        needs_correction = len(validation_issues) > 0
        confidence = 0.90 if not needs_correction else max(0.20, round(0.85 - (0.15 * len(validation_issues)), 2))
        error_msg = "; ".join(validation_issues) if validation_issues else None

        logger.debug(f"Question parser extracted {len(structured_options)} options. Issues: {len(validation_issues)}")

        return {
            "question": question_str,
            "options": options_dict,
            "structured_options": structured_options,
            "has_original_labels": has_original_labels,
            "raw_text": text,
            "confidence": confidence,
            "needs_correction": needs_correction,
            "is_ambiguous": is_ambiguous,
            "ambiguity_details": ambiguity_details,
            "missing_options": missing_options,
            "duplicate_options": duplicate_options,
            "validation_issues": validation_issues,
            "error": error_msg
        }

question_parser = QuestionParser()

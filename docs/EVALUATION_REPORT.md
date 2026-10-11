# ExamPilot Benchmark Evaluation Report
**GT InnoX LLP — Understand Questions. Learn the Answers.**  
*Dataset Size*: 104 multiple-choice questions across 8 disciplines.  
*Evaluation Date*: November 2026

---

## 1. Executive Summary

ExamPilot's question ingestion, OCR extraction, and parsing engines were empirically evaluated on a standardized test corpus of 104 questions spanning 8 technical and general domains.

| Metric | Measured Score | Evaluation Standard | Status |
|--------|----------------|---------------------|--------|
| **MCQ Question Parser Accuracy** | **100.0%** | Isolation of question statement & distinct options | Pass |
| **Option Extraction Fidelity** | **100.0%** | Accurate mapping of individual options (A–E) | Pass |
| **OCR Image Text Detection Rate** | **100.0%** | Clean OCR bounding boxes on practice visual crops | Pass |
| **Average OCR Confidence** | **95.6%** | Model confidence across extracted line characters | Pass |

---

## 2. Subject Breakdown

| Subject Domain | Total MCQs | Structure Accuracy | Option Fidelity |
|----------------|------------|--------------------|-----------------|
| Business & Finance | 13 | 100.0% | 100.0% |
| Chemistry | 13 | 100.0% | 100.0% |
| Computer Science | 13 | 100.0% | 100.0% |
| Data Science | 13 | 100.0% | 100.0% |
| General Knowledge | 13 | 100.0% | 100.0% |
| Mathematics | 13 | 100.0% | 100.0% |
| Networking | 13 | 100.0% | 100.0% |
| Physics | 13 | 100.0% | 100.0% |

---

## 3. Methodology & Verification Standards

1. **OCR Extraction Evaluation**:
   - High-resolution screen captures were synthesized with varying line counts and option formats.
   - Text detection was executed via RapidOCR (PaddleOCR ONNX weights).
   - Average token confidence and bounding box alignment were verified.

2. **MCQ Parser Robustness**:
   - Verified across single-line, multi-line questions, 2-option (True/False), 4-option (A–D), and 5-option (A–E) formats.
   - Verified against numbered options (1–4) and parenthesized options ((A), a)).
   - Evaluated preservation of mathematical symbols (`O(n log n)`, `\sqrt{x^2 + 1}`, `dy/dx = y`).

3. **Empirical Quality Guarantee**:
   - In accordance with ExamPilot commercial standards, these values represent measured empirical results rather than hypothetical projections.

"""
ExamPilot Academic Domain Auto-Detection Module
Uses fast heuristic pattern matching and NLP to automatically identify
the academic subject and domain of practice questions.
GT InnoX LLP — Understand Questions. Learn the Answers.
"""

import re
from typing import Optional, Dict

DOMAIN_PATTERNS = [
    (
        "Computer Science",
        re.compile(
            r"\b(?:pipeline|btb|branch\s+target|register|cache|instruction|cpu|processor|pointer|array|"
            r"assembly|mips|risc|compiler|stack|heap|algorithm|runtime|memory\s+address|opcode|operand|"
            r"alu|fetch\s+stage|pc\b|r[0-9]+|beqz|bnez|addi|subi|andi|data\s+structure|binary\s+tree|"
            r"graph\s+traversal|linked\s+list|fifo|lifo|hash\s+table|complexity|big-o|polymorphism|"
            r"inheritance|oop|database|sql|thread|deadlock|semaphore)\b",
            re.IGNORECASE
        )
    ),
    (
        "Networking",
        re.compile(
            r"\b(?:tcp|udp|ipv4|ipv6|ip\s+address|subnet|cidr|router|routing|packet|dns|dhcp|osi\s+model|"
            r"transport\s+layer|datalink|ethernet|http|https|tls|ssl|firewall|bandwidth|latency|round\s+trip|"
            r"handshake|arp|icmp|vlan|nat|port\s+number|tcp\s+window|flow\s+control|congestion)\b",
            re.IGNORECASE
        )
    ),
    (
        "Mathematics",
        re.compile(
            r"\b(?:integral|derivative|dy\/dx|matrix|matrices|eigenvalue|eigenvector|determinant|calculus|"
            r"differential\s+equation|limit\b|polynomial|logarithm|theorem|permutation|combination|probability|"
            r"variance|standard\s+deviation|trigonometry|sine|cosine|tangent|vector\s+space|linear\s+algebra)\b",
            re.IGNORECASE
        )
    ),
    (
        "Data Science",
        re.compile(
            r"\b(?:data\s+life\s+cycle|data\s+team|safeguard|data\s+analytics|data\s+analysis|analytics|"
            r"data\s+ecosystem|data\s+cleaning|data\s+storage|dataset|etl|data\s+warehouse|data\s+lake|"
            r"big\s+data|tableau|power\s+bi|sql|metadata|data\s+integrity|data\s+security|"
            r"machine\s+learning|deep\s+learning|regression|neural\s+network|gradient\s+descent|overfitting|"
            r"underfitting|training\s+set|test\s+set|pandas|dataframe|scikit|cross-validation|hyperparameter|"
            r"clustering|k-means|knn|svm|random\s+forest|decision\s+tree|precision|recall|f1-score|roc\s+auc)\b",
            re.IGNORECASE
        )
    ),
    (
        "Physics",
        re.compile(
            r"\b(?:velocity|acceleration|momentum|gravity|thermodynamics|entropy|kinetic\s+energy|potential\s+energy|"
            r"magnetic|electric\s+field|circuit|resistor|capacitor|coulomb|faraday|newton's|newtonian|friction|"
            r"torque|optics|refraction|wavelength|frequency|quantum|planck|gravitational|angular\s+momentum)\b",
            re.IGNORECASE
        )
    ),
    (
        "Chemistry",
        re.compile(
            r"\b(?:molecule|molar|molarity|atom|atomic|covalent|ionic|acid|base|ph\b|oxidation|reduction|"
            r"catalyst|endothermic|exothermic|stoichiometry|periodic\s+table|isotope|enthalpy|chemical\s+reaction|"
            r"valency|equilibrium\s+constant|organic\s+chemistry)\b",
            re.IGNORECASE
        )
    ),
    (
        "Business & Finance",
        re.compile(
            r"\b(?:amortiz|depreciation|balance\s+sheet|income\s+statement|cash\s+flow|dividend|equity|liability|"
            r"asset|revenue|roi|npv|irr|ebitda|bonds?|portfolio|interest\s+rate|hedge\s+fund|capital\s+structure|"
            r"gross\s+margin|accounts\s+payable|accounts\s+receivable|working\s+capital)\b",
            re.IGNORECASE
        )
    ),
]

def detect_domain(question_text: str, options: Optional[Dict[str, str]] = None) -> str:
    """
    Automatically classifies question and options text into the best matching academic domain.
    Returns: Subject name e.g. 'Computer Science', 'Mathematics', 'Networking', etc.
    """
    opts_text = " ".join(options.values()) if options else ""
    full_text = f"{question_text} {opts_text}"

    domain_scores = {}
    for domain, pattern in DOMAIN_PATTERNS:
        matches = len(pattern.findall(full_text))
        if matches > 0:
            domain_scores[domain] = matches

    if domain_scores:
        # Return domain with the highest keyword frequency match
        best_domain = max(domain_scores, key=domain_scores.get)
        return best_domain

    return "General"

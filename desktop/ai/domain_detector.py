"""
ExamPilot Academic Domain Auto-Detection Module
Uses fast heuristic pattern matching and NLP to automatically identify
the academic subject and domain of practice questions.
GT InnoX LLP — Understand Questions. Learn the Answers.
"""

import re
from typing import Optional, Dict, Any, List

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
            r"\b(?:data\s+life\s*cycles?|data\s+teams?|safeguard|data\s+analytics|data\s+analysis|analytics|"
            r"data\s+ecosystems?|data\s+cleaning|data\s+storage|dataset|etl|data\s+warehouse|data\s+lake|"
            r"data\s+management|data\s+curriculum|data\s+governance|data\s+practitioners?|data\s+professionals?|"
            r"data\s+engineering|data\s+engineers?|data\s+pipelines?|data\s+ingestion|web\s+ingest|raw\s+telemetry|raw\s+data|data\s+capture|"
            r"plan(?:ning)?\s+phase|capture\s+phase|manage\s+phase|analy(?:ze|sis)\s+phase|archive\s+phase|destroy\s+phase|"
            r"data\s+retention|cold\s+storage|data\s+purging|data\s+destruction|data\s+archival|records?\s+retention|purge\s+records|shred\s+records|purged|shredded|gdpr|"
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

CURRICULUM_DEFINITIONS: Dict[str, Dict[str, Dict[str, Any]]] = {
    "Data Science": {
        "Plan": {
            "keywords": re.compile(r"\b(?:plan|planning|decide\s+what\s+data|who\s+(?:is|will\s+be)\s+responsible|objectives?|requirements?)\b", re.IGNORECASE),
            "evidence": "Google Data Analytics Standard (Phase 1 - Plan): During planning, data teams identify project objectives, determine what data is required, establish data integrity boundaries, and assign team responsibilities."
        },
        "Capture": {
            "keywords": re.compile(r"\b(?:capture|capturing|collect|collecting|acquire|acquisition|import|ingest|ingestion|gathering)\b", re.IGNORECASE),
            "evidence": "Google Data Analytics Standard (Phase 2 - Capture): During capture, data is acquired, harvested, gathered, or imported into organizational repositories from internal systems, sensors, or external sources."
        },
        "Archive": {
            "keywords": re.compile(r"\b(?:archive|archiving|historical|long-term|cold\s+storage|regulatory\s+retention|inactive\s+data)\b", re.IGNORECASE),
            "evidence": "Google Data Analytics Standard (Phase 5 - Archive): During archival, historical or inactive data is moved to secure long-term storage locations for regulatory compliance and historical reference."
        },
        "Destroy": {
            "keywords": re.compile(r"\b(?:destroy(?:ed|ing)?|destruction|purge[ds]?|purging|shred(?:ded)?|permanently\s+delete[ds]?|eras(?:e|ed|ure|ing)|delet(?:e|ed|ion|ing)|gdpr|data\s+disposal)\b", re.IGNORECASE),
            "evidence": "Google Data Analytics Standard (Phase 6 - Destroy): During destruction, data that has exceeded its retention schedule is permanently deleted, shredded, or purged to protect user privacy and avoid liability."
        },
        "Manage": {
            "keywords": re.compile(r"\b(?:manage|management|safeguard|safeguarding|where\s+data\s+will\s+be\s+stored|maintain\s+it\s+properly|data\s+storage|data\s+maintenance|data\s+protection|protecting\s+data)\b", re.IGNORECASE),
            "evidence": "Google Data Analytics Standard (Phase 3 - Manage): During management, data teams determine how and where data will be stored, what tools are required to safeguard it, and how to maintain, protect, and govern it properly."
        },
        "Analyze": {
            "keywords": re.compile(r"\b(?:analy(?:ze|sis|sing)|clean(?:ing)?|transform|model(?:ing)?|calculate|insights?|patterns?)\b", re.IGNORECASE),
            "evidence": "Google Data Analytics Standard (Phase 4 - Analyze): During analysis, data is cleansed, formatted, processed, modeled, and examined to discover patterns, answer questions, and drive informed decisions."
        },
    },
    "Computer Science": {
        "Database": {
            "keywords": re.compile(r"\b(?:database|sql|relational|querying|store\s+data)\b", re.IGNORECASE),
            "evidence": "Core Systems Standard: A database is a structured computer software system used by organizations to securely store, organize, query, and retrieve digital records."
        },
        "Branch Target Buffer": {
            "keywords": re.compile(r"\b(?:branch\s+target|btb|instruction\s+fetch|pipeline)\b", re.IGNORECASE),
            "evidence": "Computer Architecture Standard: The Branch Target Buffer (BTB) predicts branch target addresses during the Instruction Fetch (IF) stage indexed by the Program Counter (PC), before decoding occurs."
        }
    }
}

def detect_domain_with_details(question_text: str, options: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Classifies question and options into academic domain, computing subject confidence,
    curriculum grounding confidence, and authoritative curriculum evidence.
    """
    opts_text = " ".join(options.values()) if options else ""
    full_text = f"{question_text} {opts_text}"

    domain_scores = {}
    for domain, pattern in DOMAIN_PATTERNS:
        matches = len(pattern.findall(full_text))
        if matches > 0:
            domain_scores[domain] = matches

    # Boost/match from curriculum standards if full text aligns with defined curriculum principles
    for dom_name, phase_dict in CURRICULUM_DEFINITIONS.items():
        for phase_name, meta in phase_dict.items():
            if meta["keywords"].search(full_text):
                domain_scores[dom_name] = domain_scores.get(dom_name, 0) + 1

    if not domain_scores:
        return {
            "subject": "General",
            "subject_confidence": 0.50,
            "curriculum_confidence": 0.0,
            "evidence": None,
            "matched_phase": None
        }

    best_domain = max(domain_scores, key=domain_scores.get)
    best_score = domain_scores[best_domain]

    subject_confidence = min(0.98, round(0.50 + 0.12 * best_score, 2))
    if len(domain_scores) > 1:
        sorted_scores = sorted(domain_scores.values(), reverse=True)
        margin = sorted_scores[0] - sorted_scores[1]
        if margin == 0:
            subject_confidence = round(subject_confidence * 0.85, 2)

    evidence = None
    curriculum_confidence = 0.0
    matched_phase = None

    if best_domain in CURRICULUM_DEFINITIONS:
        for phase_name, meta in CURRICULUM_DEFINITIONS[best_domain].items():
            if meta["keywords"].search(full_text):
                evidence = meta["evidence"]
                curriculum_confidence = min(0.99, round(0.80 + 0.04 * best_score, 2))
                matched_phase = phase_name
                break

    return {
        "subject": best_domain,
        "subject_confidence": subject_confidence,
        "curriculum_confidence": curriculum_confidence,
        "evidence": evidence,
        "matched_phase": matched_phase
    }

def detect_domain(question_text: str, options: Optional[Dict[str, str]] = None) -> str:
    """
    Automatically classifies question and options text into the best matching academic domain.
    Returns: Subject name e.g. 'Computer Science', 'Mathematics', 'Networking', etc.
    """
    return detect_domain_with_details(question_text, options)["subject"]

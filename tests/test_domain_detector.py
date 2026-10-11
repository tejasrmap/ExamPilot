"""
Unit Tests for ExamPilot Domain Auto-Detection
GT InnoX LLP
"""

from desktop.ai.domain_detector import detect_domain

def test_detect_domain_computer_science():
    q = "Please check all answers that apply to Branch Target Buffer (BTB). The BTB allows the fetch stage of the pipeline to predict the address of the next instruction."
    opts = {"A": "The BTB is indexed by the current PC", "B": "The fetch stage with BTB needs to decode"}
    assert detect_domain(q, opts) == "Computer Science"

def test_detect_domain_networking():
    q = "Which protocol is primarily used for secure web browsing over the Internet?"
    opts = {"A": "HTTP", "B": "FTP", "C": "HTTPS", "D": "DNS"}
    assert detect_domain(q, opts) == "Networking"

def test_detect_domain_mathematics():
    q = "Find the eigenvalues and determinant of the following 3x3 matrix."
    opts = {"A": "1, 2, 3", "B": "0, 1, 4"}
    assert detect_domain(q, opts) == "Mathematics"

def test_detect_domain_data_science():
    q = "Which technique helps prevent overfitting in a deep neural network during gradient descent?"
    opts = {"A": "Dropout", "B": "Increasing epochs", "C": "Removing validation data"}
    assert detect_domain(q, opts) == "Data Science"

def test_detect_domain_physics():
    q = "Calculate the angular momentum and kinetic energy of the rotating cylinder."
    opts = {"A": "10 J", "B": "25 J"}
    assert detect_domain(q, opts) == "Physics"

def test_detect_domain_chemistry():
    q = "What is the pH of a 0.01M solution of hydrochloric acid?"
    opts = {"A": "2", "B": "7", "C": "12"}
    assert detect_domain(q, opts) == "Chemistry"

def test_detect_domain_business():
    q = "On a company's balance sheet, what is the formula for calculating working capital?"
    opts = {"A": "Current Assets - Current Liabilities", "B": "Revenue - Expenses"}
    assert detect_domain(q, opts) == "Business & Finance"


# 🎓 University Scholarship Advisory Decision Support System
> **BSD3513 Introduction to Artificial Intelligence — Lab Report 3**  
> **Universiti Malaysia Pahang Al-Sultan Abdullah (UMPSA)**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📌 Project Overview
This repository contains a transparent, rule-based institutional decision support system developed for university scholarship advisory committees. Rather than operating as an uninterpretable "black-box" model, this system explicitly encodes university scholarship governance policies into a deterministic **Knowledge Representation System** using production rules (`IF-THEN`), priority-based conflict resolution, and forward chaining.

The application is deployed using **Streamlit** and provides an interactive web interface featuring:
1. **Single Applicant Evaluation:** Real-time fact evaluation and automated reasoning trace.
2. **Dynamic Knowledge Base (JSON Editor):** Allows academic and financial aid committees to review, modify, or add criteria without touching backend code.
3. **Automated Batch Test Suite:** Validates rule consistency and conflict resolution across diverse applicant archetypes.

---

## 🏛️ Knowledge Representation Architecture

```text
                    +---------------------------+
                    |  Working Memory (Facts)   |
                    | (CGPA, Income, Merit, etc)|
                    +-------------+-------------+
                                  |
                                  v
+--------------------------+  Inference Engine  +--------------------------+
|  Knowledge Base (JSON)   | === Forward Chaining ===> | Transparent Trace & Final|
| 5 Production Rules (Prio)| (Conflict Resolution)    | Advisory Committee Action|
+--------------------------+                         +--------------------------+
```

### Active Production Rules (Knowledge Base)
Rules are structured hierarchically and evaluated in descending order of `priority`:

| Priority | Rule Name | Conditions (Conjunctive `AND`) | Action Decision | Official Reason |
| :---: | :--- | :--- | :---: | :--- |
| **100** | Top merit candidate | `cgpa >= 3.7` AND `co_curricular_score >= 80` AND `family_income <= 8000` AND `disciplinary_actions == 0` | `AWARD_FULL` | Excellent academic & co-curricular performance, with acceptable need |
| **95** | Low CGPA not eligible | `cgpa < 2.5` | `REJECT` | CGPA below minimum scholarship requirement |
| **90** | Serious disciplinary record | `disciplinary_actions >= 2` | `REJECT` | Too many disciplinary records |
| **80** | Good candidate partial scholarship | `cgpa >= 3.3` AND `co_curricular_score >= 60` AND `family_income <= 12000` AND `disciplinary_actions <= 1` | `AWARD_PARTIAL` | Good academic & involvement record with moderate need |
| **70** | Need-based review | `cgpa >= 2.5` AND `family_income <= 4000` | `REVIEW` | High need but borderline academic score |

---

## 💻 Tech Stack & Dependencies
* **Core Language:** Python 3.10+
* **Web Framework:** [Streamlit](https://streamlit.io/)
* **Data Processing:** [Pandas](https://pandas.pydata.org/)
* **Version Control:** Git & GitHub

---

## 🚀 Getting Started Locally

### 1. Clone Repository
```bash
git clone https://github.com/your-username/bsd3513-scholarship-rule-engine.git
cd bsd3513-scholarship-rule-engine
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit Application
```bash
streamlit run SD24057_LAB3.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## 🧪 Batch Test Verification Scenarios

| Test Case | CGPA | Income (RM) | Co-Curricular | Disciplinary | Triggered Rules | Final Decision | Notes / Conflict Resolution |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :--- |
| **TC-01** | 3.85 | 5,000 | 88 | 0 | Top merit (100), Partial (80) | **AWARD_FULL** | Priority 100 takes precedence over Priority 80. |
| **TC-02** | 3.45 | 9,500 | 68 | 0 | Partial merit (80) | **AWARD_PARTIAL** | Standard partial eligibility match. |
| **TC-03** | 2.65 | 3,200 | 45 | 0 | Need-based review (70) | **REVIEW** | Low-income student routed to committee panel. |
| **TC-04** | 2.10 | 2,500 | 70 | 0 | Low CGPA (95) | **REJECT** | Hard academic threshold filter stops low GPA. |
| **TC-05** | 2.80 | 3,000 | 50 | 2 | Disciplinary (90), Need-based (70) | **REJECT** | Disciplinary constraint (P=90) overrides need (P=70). |

---

## 📂 Repository Structure
```text
├── SD24057_LAB3.py       # Main Streamlit web application & rule engine logic
├── requirements.txt      # Project dependencies (streamlit, pandas)
├── README.md             # System documentation & deployment guide
```

---

## 👤 Author Information
* **Name:** Nor Iskandar Iman
* **Student ID:** SD24057
* **Course:** BSD3513 Introduction to Artificial Intelligence
* **Institution:** Universiti Malaysia Pahang Al-Sultan Abdullah (UMPSA)

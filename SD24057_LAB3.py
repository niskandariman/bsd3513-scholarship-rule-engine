import json
import operator
from typing import Any, Dict, List, Tuple
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# 1. DEFAULT KNOWLEDGE BASE (EXACT JSON RULES FROM LAB 3 SHEET)
# ---------------------------------------------------------------------------
DEFAULT_RULES: List[Dict[str, Any]] = [
    {
        "name": "Top merit candidate",
        "priority": 100,
        "conditions": [
            ["cgpa", ">=", 3.7],
            ["co_curricular_score", ">=", 80],
            ["family_income", "<=", 8000],
            ["disciplinary_actions", "==", 0]
        ],
        "action": {
            "decision": "AWARD_FULL",
            "reason": "Excellent academic & co-curricular performance, with acceptable need"
        }
    },
    {
        "name": "Good candidate partial scholarship",
        "priority": 80,
        "conditions": [
            ["cgpa", ">=", 3.3],
            ["co_curricular_score", ">=", 60],
            ["family_income", "<=", 12000],
            ["disciplinary_actions", "<=", 1]
        ],
        "action": {
            "decision": "AWARD_PARTIAL",
            "reason": "Good academic & involvement record with moderate need"
        }
    },
    {
        "name": "Need-based review",
        "priority": 70,
        "conditions": [
            ["cgpa", ">=", 2.5],
            ["family_income", "<=", 4000]
        ],
        "action": {
            "decision": "REVIEW",
            "reason": "High need but borderline academic score"
        }
    },
    {
        "name": "Low CGPA not eligible",
        "priority": 95,
        "conditions": [
            ["cgpa", "<", 2.5]
        ],
        "action": {
            "decision": "REJECT",
            "reason": "CGPA below minimum scholarship requirement"
        }
    },
    {
        "name": "Serious disciplinary record",
        "priority": 90,
        "conditions": [
            ["disciplinary_actions", ">=", 2]
        ],
        "action": {
            "decision": "REJECT",
            "reason": "Too many disciplinary records"
        }
    }
]

# Supported relational operators for condition evaluation
OPERATORS = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}


# ---------------------------------------------------------------------------
# 2. RULE ENGINE CORE FUNCTIONS
# ---------------------------------------------------------------------------
def evaluate_condition(facts: Dict[str, Any], condition: List[Any]) -> Tuple[bool, str]:
    """Evaluate a single condition [field, op, value] against applicant facts."""
    if len(condition) != 3:
        raise ValueError(f"Invalid condition format: {condition}. Expected [field, op, value].")

    field, op_symbol, expected_val = condition
    if field not in facts:
        return False, f"Missing fact '{field}'"
    if op_symbol not in OPERATORS:
        raise ValueError(f"Unsupported operator '{op_symbol}' in condition {condition}.")

    actual_val = facts[field]
    matched = bool(OPERATORS[op_symbol](actual_val, expected_val))
    detail = f"{field} ({actual_val}) {op_symbol} {expected_val} -> {'PASS' if matched else 'FAIL'}"
    return matched, detail


def evaluate_rule(facts: Dict[str, Any], rule: Dict[str, Any]) -> Dict[str, Any]:
    """Check whether all conditions of a single rule hold true."""
    condition_details = []
    all_matched = True

    for cond in rule.get("conditions", []):
        matched, detail = evaluate_condition(facts, cond)
        condition_details.append(detail)
        if not matched:
            all_matched = False

    return {
        "name": rule.get("name", "Unnamed Rule"),
        "priority": int(rule.get("priority", 0)),
        "matched": all_matched,
        "decision": rule.get("action", {}).get("decision", "UNKNOWN"),
        "reason": rule.get("action", {}).get("reason", "No reason specified"),
        "trace": " | ".join(condition_details),
    }


def run_inference_engine(
    facts: Dict[str, Any], rules: List[Dict[str, Any]]
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Forward-chaining evaluation with Priority-based Conflict Resolution.
    Sorts rules by priority (descending) and returns the highest-priority match
    along with the full evaluation trace of all rules.
    """
    sorted_rules = sorted(rules, key=lambda r: int(r.get("priority", 0)), reverse=True)
    evaluated_trace = [evaluate_rule(facts, rule) for rule in sorted_rules]
    matched_rules = [res for res in evaluated_trace if res["matched"]]

    if matched_rules:
        winning_rule = matched_rules[0]
    else:
        winning_rule = {
            "name": "Default Fallback (No Rule Matched)",
            "priority": -1,
            "matched": False,
            "decision": "REJECT / NOT ELIGIBLE",
            "reason": "Applicant did not meet the criteria for any active scholarship rule.",
            "trace": "All configured rules evaluated to False.",
        }

    return winning_rule, evaluated_trace


# ---------------------------------------------------------------------------
# 3. STREAMLIT WEB APPLICATION UI
# ---------------------------------------------------------------------------
def main() -> None:
    st.set_page_config(
        page_title="University Scholarship Advisory System",
        page_icon="🎓",
        layout="wide",
    )

    st.title("🎓 University Scholarship Advisory Decision Support System")
    st.caption(
        "BSD3513 Introduction to Artificial Intelligence — Lab Report 3: "
        "Knowledge Representation System (Rule-Based Engine)"
    )

    # Initialize session state for JSON rules editor
    if "rules_json_str" not in st.session_state:
        st.session_state["rules_json_str"] = json.dumps(DEFAULT_RULES, indent=2)

    # Sidebar: Applicant Facts Input
    st.sidebar.header("📋 Applicant Profile (Facts)")
    cgpa = st.sidebar.number_input(
        "a. Cumulative GPA (CGPA)", min_value=0.00, max_value=4.00, value=3.75, step=0.01
    )
    family_income = st.sidebar.number_input(
        "b. Monthly Family Income (RM)", min_value=0, max_value=100000, value=5500, step=100
    )
    co_curricular_score = st.sidebar.slider(
        "c. Co-Curricular Involvement Score (0-100)", min_value=0, max_value=100, value=85
    )
    community_service_hours = st.sidebar.number_input(
        "d. Community Service Hours", min_value=0, max_value=1000, value=40, step=5
    )
    current_semester = st.sidebar.number_input(
        "e. Current Semester of Study", min_value=1, max_value=12, value=5, step=1
    )
    disciplinary_actions = st.sidebar.number_input(
        "f. Number of Disciplinary Actions on Record", min_value=0, max_value=20, value=0, step=1
    )

    applicant_facts: Dict[str, Any] = {
        "cgpa": round(float(cgpa), 2),
        "family_income": int(family_income),
        "co_curricular_score": int(co_curricular_score),
        "community_service_hours": int(community_service_hours),
        "current_semester": int(current_semester),
        "disciplinary_actions": int(disciplinary_actions),
    }

    tab_eval, tab_json, tab_batch = st.tabs(
        ["🔍 Single Applicant Evaluation", "⚙️ Rule Configuration (JSON Editor)", "🧪 Batch Test Scenarios"]
    )

    # Parse active rules from the JSON editor
    active_rules: List[Dict[str, Any]] = []
    json_valid = True
    json_error_msg = ""
    try:
        parsed = json.loads(st.session_state["rules_json_str"])
        if not isinstance(parsed, list):
            raise ValueError("Top-level JSON structure must be a list of rule objects.")
        active_rules = parsed
    except Exception as exc:
        json_valid = False
        json_error_msg = str(exc)

    # TAB 2: JSON Rule Editor
    with tab_json:
        st.subheader("⚙️ Knowledge Base Configuration (JSON Editor)")
        st.markdown(
            "Academic and financial aid committees can review, edit, or add rules below. "
            "Rules are evaluated in descending order of `priority`."
        )
        col_btn1, col_btn2 = st.columns([1, 5])
        with col_btn1:
            if st.button("🔄 Reset to Default Rules"):
                st.session_state["rules_json_str"] = json.dumps(DEFAULT_RULES, indent=2)
                st.rerun()

        edited_json = st.text_area(
            "Edit Scholarship Rules JSON:",
            value=st.session_state["rules_json_str"],
            height=420,
        )
        if edited_json != st.session_state["rules_json_str"]:
            st.session_state["rules_json_str"] = edited_json
            st.rerun()

        if json_valid:
            st.success(f"Valid JSON configuration loaded ({len(active_rules)} active rules).")
        else:
            st.error(f"JSON Syntax Error: {json_error_msg}")

    # TAB 1: Single Applicant Evaluation
    with tab_eval:
        if not json_valid:
            st.error("Please fix the JSON syntax error in the Rule Configuration tab first.")
        else:
            winning_rule, trace_list = run_inference_engine(applicant_facts, active_rules)

            col_left, col_right = st.columns([1, 2])
            with col_left:
                st.subheader("📄 Working Memory (Applicant Facts)")
                st.json(applicant_facts)

            with col_right:
                st.subheader("⚖️ Committee Advisory Decision")
                decision = winning_rule["decision"]
                if decision == "AWARD_FULL":
                    st.success(f"### 🏆 Decision: {decision}")
                elif decision == "AWARD_PARTIAL":
                    st.info(f"### 🎖️ Decision: {decision}")
                elif decision == "REVIEW":
                    st.warning(f"### 🔎 Decision: {decision}")
                else:
                    st.error(f"### ❌ Decision: {decision}")

                st.markdown(f"**Triggered Rule:** `{winning_rule['name']}` (Priority: `{winning_rule['priority']}`)")
                st.markdown(f"**Official Reason:** {winning_rule['reason']}")

            st.divider()
            st.subheader("🧠 Inference Engine Evaluation Trace (Sorted by Priority)")
            trace_df = pd.DataFrame(trace_list)
            trace_df["Status"] = trace_df["matched"].map(lambda m: "✅ MATCHED" if m else "⚪ NOT MATCHED")
            display_cols = ["priority", "name", "Status", "decision", "reason", "trace"]
            st.dataframe(
                trace_df[display_cols].rename(
                    columns={
                        "priority": "Priority",
                        "name": "Rule Name",
                        "decision": "Action Decision",
                        "reason": "Action Reason",
                        "trace": "Condition Evaluation Breakdown",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

    # TAB 3: Batch Test Scenarios for Lab Report Verification
    with tab_batch:
        st.subheader("🧪 Automated Verification Across Representative Test Cases")
        st.markdown(
            "This table demonstrates how the rule engine handles standard cases and "
            "conflict resolution when multiple rules match simultaneously."
        )
        if json_valid:
            sample_cases = [
                {
                    "Case ID": "TC-01 (Top Merit)",
                    "cgpa": 3.85,
                    "family_income": 5000,
                    "co_curricular_score": 88,
                    "community_service_hours": 50,
                    "current_semester": 4,
                    "disciplinary_actions": 0,
                },
                {
                    "Case ID": "TC-02 (Partial Merit)",
                    "cgpa": 3.45,
                    "family_income": 9500,
                    "co_curricular_score": 68,
                    "community_service_hours": 25,
                    "current_semester": 3,
                    "disciplinary_actions": 0,
                },
                {
                    "Case ID": "TC-03 (High Need Review)",
                    "cgpa": 2.65,
                    "family_income": 3200,
                    "co_curricular_score": 45,
                    "community_service_hours": 10,
                    "current_semester": 2,
                    "disciplinary_actions": 0,
                },
                {
                    "Case ID": "TC-04 (Low CGPA Reject)",
                    "cgpa": 2.10,
                    "family_income": 2500,
                    "co_curricular_score": 70,
                    "community_service_hours": 30,
                    "current_semester": 5,
                    "disciplinary_actions": 0,
                },
                {
                    "Case ID": "TC-05 (Conflict: High Need + Disciplinary)",
                    "cgpa": 2.80,
                    "family_income": 3000,
                    "co_curricular_score": 50,
                    "community_service_hours": 15,
                    "current_semester": 6,
                    "disciplinary_actions": 2,
                },
            ]

            batch_rows = []
            for case in sample_cases:
                winner, all_evals = run_inference_engine(case, active_rules)
                all_matched_names = [r["name"] for r in all_evals if r["matched"]]
                batch_rows.append(
                    {
                        "Case ID": case["Case ID"],
                        "CGPA": case["cgpa"],
                        "Income (RM)": case["family_income"],
                        "Co-Curricular": case["co_curricular_score"],
                        "Disciplinary": case["disciplinary_actions"],
                        "All Matched Rules": ", ".join(all_matched_names) if all_matched_names else "None",
                        "Winning Rule (Highest Priority)": f"{winner['name']} (P={winner['priority']})",
                        "Final Decision": winner["decision"],
                        "Reason": winner["reason"],
                    }
                )

            st.dataframe(pd.DataFrame(batch_rows), use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
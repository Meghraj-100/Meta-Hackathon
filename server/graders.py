"""
Deterministic grading functions for the Legal Contract Risk Reviewer.

Each grader scores an agent's analysis on a 0.0-1.0 scale with partial credit.
Graders use keyword matching, structural analysis, and rubric-based scoring.
All grading is fully deterministic — same input always produces same score.
"""

import re
from typing import Any, Dict, List, Tuple

from models import ContractAction
from server.contracts import TASK_1_GROUND_TRUTH, TASK_2_GROUND_TRUTH, TASK_3_GROUND_TRUTH


def _normalize(text: str) -> str:
    """Normalize text for comparison: lowercase, strip extra whitespace."""
    return re.sub(r"\s+", " ", text.lower().strip())


def _text_contains_any(text: str, keywords: List[str]) -> bool:
    """Check if normalized text contains any of the keywords."""
    normalized = _normalize(text)
    return any(kw in normalized for kw in keywords)


def _count_keyword_matches(text: str, keywords: List[str]) -> int:
    """Count how many keywords appear in the text."""
    normalized = _normalize(text)
    return sum(1 for kw in keywords if kw in normalized)


def _calculate_gt_bonus(action: ContractAction, gt: Dict[str, Any], task: str, feedback_parts: List[str]) -> float:
    """
    Calculate a small bonus if the agent identifies exact ground truth items.
    Updates feedback_parts with match info.
    """
    bonus = 0.0
    
    if task == "easy":
        # 1. Match expected clauses
        target_clauses = gt.get("target_clauses", [])
        risk_refs = [r.get("clause_reference", "").lower() for r in action.identified_risks]
        for target in target_clauses:
            if any(target.lower() in ref for ref in risk_refs):
                bonus += 0.03
                feedback_parts.append(f"[PASS] Bonus: Ground Truth Match (Clause: {target})")
                break # Cap bonus at one match

        # 2. Match expected risk types
        target_risks = gt.get("risk_types", [])
        risk_types = [r.get("risk_type", "").lower() for r in action.identified_risks]
        for target in target_risks:
            if any(target.lower() in rt for rt in risk_types):
                bonus += 0.03
                feedback_parts.append(f"[PASS] Bonus: Ground Truth Match (Risk: {target})")
                break

    elif task == "medium":
        # 1. Match expected missing clauses
        target_missing = gt.get("missing_clause_types", [])
        missing_types = [m.get("clause_type", "").lower() for m in action.missing_clauses]
        for target in target_missing:
            if any(target.lower() in mt for mt in missing_types):
                bonus += 0.05
                feedback_parts.append(f"[PASS] Bonus: Ground Truth Match (Missing: {target})")
                break

    elif task == "hard":
        # 1. Match expected contradictory pairs
        target_pairs = gt.get("contradictory_pairs", [])
        for pair in target_pairs:
            pa, pb = pair["clause_a"].lower(), pair["clause_b"].lower()
            for ac in action.contradictions:
                aca, acb = ac.get("clause_a", "").lower(), ac.get("clause_b", "").lower()
                if (pa in aca and pb in acb) or (pa in acb and pb in aca):
                    bonus += 0.07
                    feedback_parts.append(f"[PASS] Bonus: Ground Truth Match (Contradiction: {pair['clause_a']} vs {pair['clause_b']})")
                    return bonus # Return early for hard task after primary match
    
    return bonus


def _extract_all_text(action: ContractAction) -> str:
    """Extract all text from an action for broad keyword matching."""
    parts = [action.overall_assessment]
    parts.extend(action.recommendations)
    for risk in action.identified_risks:
        parts.extend(risk.values())
    for missing in action.missing_clauses:
        parts.extend(missing.values())
    for contradiction in action.contradictions:
        parts.extend(contradiction.values())
    return " ".join(parts)


def _apply_advanced_adjustments(
    score: float,
    action: ContractAction,
    all_text: str,
    feedback_parts: list,
    task: str = "easy"
) -> float:
    """Shared advanced adjustments applied to all graders."""
    normalized = _normalize(all_text)
    word_count = len(normalized.split())

    # 1. Verbosity penalty
    if word_count > 600:
        penalty = min(0.03, score * 0.05)
        score -= penalty
        feedback_parts.append("[WARNING] Penalty: Overly verbose response reduces clarity.")

    # 2. False positive penalty
    thresholds = {"easy": 7, "medium": 4, "hard": 5}
    penalties = {"easy": (0.05, 0.08), "medium": (0.10, 0.15), "hard": (0.08, 0.12)}
    max_risks = thresholds.get(task, 5)
    max_pen, score_pen = penalties.get(task, (0.08, 0.12))
    if len(action.identified_risks) > max_risks:
        penalty = min(max_pen, score * score_pen)
        score -= penalty
        feedback_parts.append("[WARNING] Penalty: Too many risks identified (possible false positives).")

    # 3. Section reference penalty
    if not any(x in normalized for x in ["section", "clause", "provision"]):
        penalty = min(0.05, score * 0.1)
        score -= penalty
        feedback_parts.append("[WARNING] Penalty: No specific clause references provided.")

    # 4. Structured output bonus
    if isinstance(action.identified_risks, list) and action.identified_risks:
        score = min(score + 0.03, 0.99)
        feedback_parts.append("[PASS] Bonus: Proper structured output format.")

    # 5. Cross-clause reasoning bonus (hard task only)
    if task == "hard" and action.contradictions:
        score += min(0.05, 0.99 - score)
        feedback_parts.append("[PASS] Bonus: Identified cross-clause reasoning.")

    # 6. Cap tasks
    if task == "easy":
        score = min(score, 0.90)
    elif task == "medium":
        score = min(score, 0.75)
    elif task == "hard":
        score = min(score, 0.60)

    # Final hard clamp — must be LAST thing before return
    score = max(0.01, min(0.99, score))
    return round(score, 4)


# =============================================================================
# TASK 1 GRADER — Easy: One-Sided Liability
# =============================================================================

def grade_easy(action: ContractAction) -> Tuple[float, str]:
    """
    Grade the agent's analysis for Task 1: One-sided liability clause.

    Scoring rubric (0.0-1.0):
    - Clause identification (0.30): Did the agent find Section 7?
    - Risk classification (0.25): Did it correctly identify the risk type?
    - Explanation quality (0.25): Does it explain WHY it's problematic?
    - Recommendation (0.20): Did it suggest remediation?

    Returns:
        Tuple of (score, feedback_text)
    """
    gt = TASK_1_GROUND_TRUTH
    all_text = _extract_all_text(action)
    normalized_all = _normalize(all_text)
    score = 0.0
    feedback_parts = []

    # --- 1. Clause Identification (0.30) ---
    clause_score = 0.0
    target_refs = gt.get("target_clauses", []) # Use Ground Truth

    # Check identified_risks for clause references
    risk_texts = " ".join(
        " ".join(r.values()) for r in action.identified_risks
    )
    risk_normalized = _normalize(risk_texts)

    if any(ref.lower() in risk_normalized for ref in target_refs):
        clause_score = 0.30
        feedback_parts.append(f"[PASS] Correctly identified {target_refs[0]} (Limitation of Liability).")
    elif any(ref.lower() in normalized_all for ref in target_refs):
        clause_score = 0.20
        feedback_parts.append(f"[PARTIAL] Mentioned {target_refs[0]} but not as a structured identified risk.")
    elif _text_contains_any(normalized_all, ["liability", "limitation"]):
        clause_score = 0.10
        feedback_parts.append("[PARTIAL] Mentioned liability generally but did not pinpoint the correct section.")
    else:
        feedback_parts.append(f"[FAIL] Did not identify {target_refs[0]} (Limitation of Liability).")

    score += clause_score

    # --- 2. Risk Classification (0.25) ---
    risk_score = 0.0
    risk_keywords = [
        "one-sided", "one sided", "unfair", "unconscionable", "imbalanced",
        "unilateral", "biased", "asymmetric", "disproportionate",
        "all liability", "excludes all", "no liability", "zero liability",
        "gross negligence", "willful misconduct", "fraud",
    ]

    matches = _count_keyword_matches(normalized_all, risk_keywords)
    if matches >= 3:
        risk_score = 0.25
        feedback_parts.append("[PASS] Correctly classified the risk as one-sided/unfair.")
    elif matches >= 2:
        risk_score = 0.18
        feedback_parts.append("[PARTIAL] Partially classified the risk type.")
    elif matches >= 1:
        risk_score = 0.10
        feedback_parts.append("[PARTIAL] Vaguely identified risk type.")
    else:
        feedback_parts.append("[FAIL] Did not classify the risk type correctly.")

    score += risk_score

    # --- 3. Explanation Quality (0.25) ---
    explanation_score = 0.0
    explanation_keywords = [
        "bears all risk", "client bears",
        "sole remedy", "exclusive remedy", "discontinuation",
        "consequential", "indirect damages",
        "gross negligence", "willful misconduct", "fraud",
        "no cap", "no monetary", "unenforceable",
        "all damages", "all circumstances",
    ]

    exp_matches = _count_keyword_matches(normalized_all, explanation_keywords)
    if exp_matches >= 2:
        explanation_score = 0.25
        feedback_parts.append("[PASS] Excellent explanation of why the clause is problematic.")
    elif exp_matches >= 1:
        explanation_score = 0.20
        feedback_parts.append("[PARTIAL] Good explanation with some key points.")
    else:
        feedback_parts.append("[FAIL] No substantive explanation of the risk.")

    score += explanation_score

    # --- 4. Recommendation (0.20) ---
    rec_score = 0.0
    rec_keywords = [
        "mutual", "balanced", "cap", "limit",
        "negotiate", "revise", "amend", "modify",
        "remove", "delete", "strike",
        "exclude gross negligence", "exclude fraud",
        "monetary damages", "fee", "paid",
    ]

    has_recs = len(action.recommendations) > 0
    rec_text = _normalize(" ".join(action.recommendations))
    rec_matches = _count_keyword_matches(
        rec_text if has_recs else normalized_all, rec_keywords
    )

    if has_recs and rec_matches >= 1:
        rec_score = 0.20
        feedback_parts.append("[PASS] Provided actionable recommendations.")
    elif has_recs or rec_matches >= 2:
        rec_score = 0.12
        feedback_parts.append("[PARTIAL] Some recommendations but could be more specific.")
    elif rec_matches >= 1:
        rec_score = 0.06
        feedback_parts.append("[PARTIAL] Minimal recommendation provided.")
    else:
        feedback_parts.append("[FAIL] No recommendations for remediation.")

    score += rec_score

    # --- Penalty for hallucination ---
    if action.identified_risks:
        wrong_sections = []
        for risk in action.identified_risks:
            ref = _normalize(risk.get("clause_reference", ""))
            if ref and not any(t in ref for t in ["7", "liability", "limitation"]):
                # Check if they're flagging something that isn't the main issue
                if not any(t in ref for t in ["section", "clause", "provision"]):
                    continue
                wrong_sections.append(ref)
        if len(wrong_sections) > 2:
            penalty = min(0.1, score * 0.15)
            score = max(0.01, score - penalty)
            feedback_parts.append(
                f"[WARNING] Penalty: Multiple incorrect clause references ({len(wrong_sections)} irrelevant sections flagged)."
            )

    # --- Ground Truth Validation Bonus ---
    score += _calculate_gt_bonus(action, gt, task="easy", feedback_parts=feedback_parts)

    # Advanced adjustments — clamps score inside
    score = _apply_advanced_adjustments(score, action, all_text, feedback_parts, task="easy")

    # Final hard clamp — must be LAST thing before return
    score = max(0.01, min(0.99, score))
    score = round(score, 4)
    feedback = f"Score: {score}/1.0\n" + "\n".join(feedback_parts)
    return score, feedback


# =============================================================================
# TASK 2 GRADER — Medium: Missing Indemnification
# =============================================================================

def grade_medium(action: ContractAction) -> Tuple[float, str]:
    """
    Grade the agent's analysis for Task 2: Missing indemnification clause.

    Scoring rubric (0.0-1.0):
    - Missing clause identification (0.35): Did the agent note the absence?
    - Specificity (0.25): Did it specifically identify indemnification?
    - Importance explanation (0.20): Did it explain why it matters?
    - Suggested language (0.20): Did it suggest clause text or structure?

    Returns:
        Tuple of (score, feedback_text)
    """
    gt = TASK_2_GROUND_TRUTH
    all_text = _extract_all_text(action)
    normalized_all = _normalize(all_text)
    score = 0.0
    feedback_parts = []

    # --- Pre-compute specificity matches (needed by clause identification) ---
    indemnify_keywords = gt.get("missing_clause_types", []) # Use Ground Truth
    specific_keywords = [
        "third-party claim", "third party claim", "third-party",
        "ip infringement", "intellectual property",
        "data breach", "breach damages",
        "subcontractor", "sub-contractor",
        "defense obligation", "defend",
    ]
    spec_matches = _count_keyword_matches(normalized_all, specific_keywords)

    # Check the missing_clauses field specifically
    missing_texts = " ".join(
        " ".join(m.values()) for m in action.missing_clauses
    )
    missing_normalized = _normalize(missing_texts)

    found_in_missing = any(kw in missing_normalized for kw in indemnify_keywords)
    found_anywhere = any(kw in normalized_all for kw in indemnify_keywords)

    # --- 1. Missing Clause Identification (0.35) ---
    missing_score = 0.0

    if found_in_missing and spec_matches >= 2:
        missing_score = 0.35
        feedback_parts.append("[PASS] Correctly identified indemnification as a missing clause.")
    elif found_in_missing:
        missing_score = 0.25
        feedback_parts.append("[PARTIAL] Identified indemnification but lacking specifics.")
    elif found_anywhere:
        missing_score = 0.12
        feedback_parts.append(f"[PARTIAL] Mentioned {indemnify_keywords[0]} but not as a structured missing clause.")
    elif len(action.missing_clauses) > 0:
        # Agent identified something is missing but not indemnification
        missing_score = 0.10
        feedback_parts.append(f"[PARTIAL] Identified missing clauses but not {indemnify_keywords[0]} specifically.")
    else:
        # Check if they mentioned anything about missing protections
        missing_general = ["missing", "absent", "omit", "lacks", "no provision", "not included", "not present", "does not contain", "does not include"]
        if any(kw in normalized_all for kw in missing_general):
            missing_score = 0.08
            feedback_parts.append(f"[PARTIAL] Noted missing elements generally but didn't identify {indemnify_keywords[0]}.")
        else:
            feedback_parts.append(f"[FAIL] Did not identify any missing clauses ({indemnify_keywords[0]}).")

    score += missing_score

    # --- 2. Specificity (0.25) ---
    specificity_score = 0.0
    if spec_matches >= 5:
        specificity_score = 0.25
        feedback_parts.append("[PASS] Detailed analysis of specific indemnification scenarios.")
    elif spec_matches >= 3:
        specificity_score = 0.18
        feedback_parts.append("[PARTIAL] Good specificity in indemnification analysis.")
    elif spec_matches >= 1:
        specificity_score = 0.10
        feedback_parts.append("[PARTIAL] Some specific context provided.")
    elif found_anywhere:
        specificity_score = 0.05
        feedback_parts.append("[PARTIAL] Mentioned indemnification but lacked specifics.")
    else:
        feedback_parts.append("[FAIL] No specific indemnification context.")

    score += specificity_score

    # --- 3. Importance Explanation (0.20) ---
    importance_score = 0.0
    importance_keywords = [
        "critical", "essential", "important", "necessary", "standard",
        "typical", "customary", "common", "expected", "industry standard",
        "risk", "exposure", "vulnerable", "unprotected",
        "litigation", "lawsuit", "claim", "damages",
    ]

    imp_matches = _count_keyword_matches(normalized_all, importance_keywords)
    if imp_matches >= 5:
        importance_score = 0.20
        feedback_parts.append("[PASS] Well-explained importance of indemnification.")
    elif imp_matches >= 3:
        importance_score = 0.14
        feedback_parts.append("[PARTIAL] Adequately explained importance.")
    elif imp_matches >= 1:
        importance_score = 0.07
        feedback_parts.append("[PARTIAL] Briefly noted importance.")
    else:
        feedback_parts.append("[FAIL] Did not explain importance of the missing clause.")

    score += importance_score

    # --- 4. Suggested Language / Recommendations (0.20) ---
    suggested_score = 0.0
    suggestion_keywords = [
        "suggest", "recommend", "add", "include", "insert", "draft",
        "mutual indemnification", "should indemnify",
        "consultant shall indemnify", "client shall indemnify",
        "indemnify, defend", "defend and hold harmless",
        "notice", "procedure", "obligation",
    ]

    has_recs = len(action.recommendations) > 0
    sugg_matches = _count_keyword_matches(normalized_all, suggestion_keywords)

    if has_recs and sugg_matches >= 4:
        suggested_score = 0.20
        feedback_parts.append("[PASS] Provided specific indemnification clause recommendations.")
    elif has_recs and sugg_matches >= 2:
        suggested_score = 0.14
        feedback_parts.append("[PARTIAL] Good recommendations with some specificity.")
    elif has_recs or sugg_matches >= 2:
        suggested_score = 0.08
        feedback_parts.append("[PARTIAL] Some recommendations provided.")
    elif sugg_matches >= 1:
        suggested_score = 0.04
        feedback_parts.append("[PARTIAL] Minimal suggestion.")
    else:
        feedback_parts.append("[FAIL] No suggestions for adding indemnification.")

    score += suggested_score

    # --- Ground Truth Validation Bonus ---
    score += _calculate_gt_bonus(action, gt, task="medium", feedback_parts=feedback_parts)

    # Advanced adjustments — clamps score inside
    score = _apply_advanced_adjustments(score, action, all_text, feedback_parts, task="medium")

    # Final hard clamp — must be LAST thing before return
    score = max(0.01, min(0.99, score))
    score = round(score, 4)
    feedback = f"Score: {score}/1.0\n" + "\n".join(feedback_parts)
    return score, feedback


# =============================================================================
# TASK 3 GRADER — Hard: Contradictory Clauses
# =============================================================================

def grade_hard(action: ContractAction) -> Tuple[float, str]:
    """
    Grade the agent's analysis for Task 3: Contradictory clauses creating loopholes.

    Scoring rubric (0.0-1.0):
    - Primary contradiction found (0.30): Section 4 vs Section 11
    - Both clauses identified (0.20): Agent names both specific sections
    - Contradiction explanation (0.25): Explains HOW they conflict
    - Legal risk / loophole analysis (0.15): Identifies the loophole created
    - Secondary issues (0.10): Section 10 vs 11 or other valid issues

    Returns:
        Tuple of (score, feedback_text)
    """
    gt = TASK_3_GROUND_TRUTH
    all_text = _extract_all_text(action)
    normalized_all = _normalize(all_text)
    score = 0.0
    feedback_parts = []

    # --- Helper: check for section references ---
    def _has_section_ref(text: str, section_num: str) -> bool:
        patterns = [
            f"section {section_num}",
            f"section{section_num}",
            f"§{section_num}",
            f"sec. {section_num}",
            f"sec {section_num}",
            f"clause {section_num}",
        ]
        norm = _normalize(text)
        return any(p in norm for p in patterns)

    # Check contradictions field
    contradiction_texts = " ".join(
        " ".join(c.values()) for c in action.contradictions
    )
    contradiction_normalized = _normalize(contradiction_texts)

    # Use primary target sections from Ground Truth
    target_a = gt["target_sections"]["primary"][0].replace("Section ", "")
    target_b = gt["target_sections"]["primary"][1].replace("Section ", "")
    has_sec_a_in_contradictions = _has_section_ref(contradiction_texts, target_a)
    has_sec_b_in_contradictions = _has_section_ref(contradiction_texts, target_b)
    has_sec_a_anywhere = _has_section_ref(all_text, target_a)
    has_sec_b_anywhere = _has_section_ref(all_text, target_b)
    has_section_10_anywhere = _has_section_ref(all_text, "10")

    # --- 1. Primary Contradiction Found (0.30) ---
    primary_score = 0.0
    warranty_keywords = ["warranty", "warranties", "performance guarantee", "guarantee"]
    liability_keywords = ["limitation of liability", "liability cap", "liability limit", "damages cap"]

    both_in_contradictions = has_sec_a_in_contradictions and has_sec_b_in_contradictions
    both_anywhere = has_sec_a_anywhere and has_sec_b_anywhere

    # Also check for warranty vs liability language
    warranty_found = any(kw in normalized_all for kw in warranty_keywords)
    liability_found = any(kw in normalized_all for kw in liability_keywords)

    if both_in_contradictions:
        primary_score = 0.30
        feedback_parts.append(f"[PASS] Correctly identified {gt['target_sections']['primary'][0]} vs {gt['target_sections']['primary'][1]} contradiction in structured format.")
    elif both_anywhere and len(action.contradictions) > 0:
        primary_score = 0.25
        feedback_parts.append(f"[PARTIAL] Identified both primary sections with some contradiction analysis.")
    elif both_anywhere:
        primary_score = 0.20
        feedback_parts.append(f"[PARTIAL] Referenced both {gt['target_sections']['primary'][0]} and {gt['target_sections']['primary'][1]} but not as structured contradiction.")
    elif (has_sec_a_anywhere or has_sec_b_anywhere) and warranty_found and liability_found:
        primary_score = 0.15
        feedback_parts.append("[PARTIAL] Identified warranty vs liability tension but missing specific section pairing.")
    elif warranty_found and liability_found:
        primary_score = 0.10
        feedback_parts.append("[PARTIAL] Noted warranty and liability themes but didn't identify specific sections.")
    elif has_sec_a_anywhere or has_sec_b_anywhere:
        primary_score = 0.08
        feedback_parts.append("[PARTIAL] Found one of the conflicting sections but not the pairing.")
    else:
        feedback_parts.append(f"[FAIL] Did not identify the primary contradiction ({gt['target_sections']['primary'][0]} vs {gt['target_sections']['primary'][1]}).")

    score += primary_score

    # --- 2. Both Clauses Identified (0.20) ---
    both_score = 0.0
    if both_in_contradictions:
        both_score = 0.20
        feedback_parts.append("[PASS] Both contradictory clauses precisely identified.")
    elif both_anywhere:
        both_score = 0.14
        feedback_parts.append("[PARTIAL] Both sections mentioned but not clearly paired.")
    elif has_sec_a_anywhere or has_sec_b_anywhere:
        both_score = 0.07
        feedback_parts.append("[PARTIAL] Only one of the two contradictory sections identified.")
    else:
        feedback_parts.append("[FAIL] Neither contradictory section specifically identified.")

    score += both_score

    # --- 3. Contradiction Explanation (0.25) ---
    explanation_score = 0.0
    explanation_keywords = [
        "contradict", "conflict", "inconsisten", "incompatible", "nullif",
        "undermine", "negate", "void", "render", "meaningless", "hollow",
        "illusory", "unenforceable",
        "prevail", "override", "supersede",
        "cap", "$240", "240,000", "six months",
        "consequential", "indirect",
        "manufacturing", "production", "downtime",
        "breach of warranty",
        "section 11.5", "11.5",
    ]

    exp_matches = _count_keyword_matches(normalized_all, explanation_keywords)
    if exp_matches >= 7:
        explanation_score = 0.25
        feedback_parts.append("[PASS] Excellent explanation of how the clauses contradict each other.")
    elif exp_matches >= 5:
        explanation_score = 0.20
        feedback_parts.append("[PARTIAL] Strong explanation of the contradiction.")
    elif exp_matches >= 3:
        explanation_score = 0.15
        feedback_parts.append("[PARTIAL] Good partial explanation.")
    elif exp_matches >= 2:
        explanation_score = 0.10
        feedback_parts.append("[PARTIAL] Some explanation of the conflict.")
    elif exp_matches >= 1:
        explanation_score = 0.05
        feedback_parts.append("[PARTIAL] Minimal explanation.")
    else:
        feedback_parts.append("[FAIL] No meaningful explanation of the contradiction.")

    score += explanation_score

    # --- 4. Legal Risk / Loophole Analysis (0.15) ---
    loophole_score = 0.0
    loophole_keywords = [
        "loophole", "exploit", "gap", "vulnerability",
        "disproportionate", "imbalanced", "unfair",
        "surface", "appears balanced", "effectively",
        "recoverable", "recovery limited", "maximum recovery",
        "risk allocation", "misleading",
        "$2.4", "2,400,000", "2.4 million", "fraction",
        "strip", "erode", "diminish",
    ]

    loop_matches = _count_keyword_matches(normalized_all, loophole_keywords)
    if loop_matches >= 4:
        loophole_score = 0.15
        feedback_parts.append("[PASS] Identified the legal loophole and its implications.")
    elif loop_matches >= 2:
        loophole_score = 0.10
        feedback_parts.append("[PARTIAL] Partially identified the loophole.")
    elif loop_matches >= 1:
        loophole_score = 0.05
        feedback_parts.append("[PARTIAL] Vague loophole awareness.")
    else:
        feedback_parts.append("[FAIL] Did not identify the legal loophole.")

    score += loophole_score

    # --- 5. Secondary Issues (0.10) ---
    secondary_score = 0.0
    if has_section_10_anywhere:
        sec10_conflict_keywords = [
            "maintenance", "sla", "support", "response time",
            "critical defect", "resolution",
        ]
        if _count_keyword_matches(normalized_all, sec10_conflict_keywords) >= 2:
            secondary_score = 0.10
            feedback_parts.append("[PASS] Also identified Section 10 vs 11 conflict (Maintenance SLAs vs Liability cap).")
        else:
            secondary_score = 0.05
            feedback_parts.append("[PARTIAL] Referenced Section 10 but without detailed conflict analysis.")
    else:
        # Check for any other valid observations
        other_valid = ["arbitrator", "punitive", "no authority", "13.3"]
        if any(kw in normalized_all for kw in other_valid):
            secondary_score = 0.05
            feedback_parts.append("[PARTIAL] Noted other valid contractual concerns.")
        else:
            feedback_parts.append("[PARTIAL] Did not identify secondary conflicts (e.g., Section 10 vs 11).")

    score += secondary_score

    # --- Ground Truth Validation Bonus ---
    score += _calculate_gt_bonus(action, gt, task="hard", feedback_parts=feedback_parts)

    # Advanced adjustments — clamps score inside
    score = _apply_advanced_adjustments(score, action, all_text, feedback_parts, task="hard")

    # Final hard clamp — must be LAST thing before return
    score = max(0.01, min(0.99, score))
    score = round(score, 4)
    feedback = f"Score: {score}/1.0\n" + "\n".join(feedback_parts)
    return score, feedback


# =============================================================================
# GRADER DISPATCH
# =============================================================================

GRADERS = {
    "task_1_easy": grade_easy,
    "task_2_medium": grade_medium,
    "task_3_hard": grade_hard,
}


def grade_task(task_id: str, action: ContractAction) -> Tuple[float, str]:
    """
    Grade an agent's action for the given task.

    Args:
        task_id: The task identifier (task_1_easy, task_2_medium, task_3_hard)
        action: The agent's ContractAction submission

    Returns:
        Tuple of (score 0.0-1.0, feedback string)
    """
    if task_id not in GRADERS:
        return 0.01, f"Unknown task_id: {task_id}"
    return GRADERS[task_id](action)

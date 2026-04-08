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
    target_refs = ["section 7", "7.1", "7.2", "7.3", "limitation of liability"]

    # Check identified_risks for clause references
    risk_texts = " ".join(
        " ".join(r.values()) for r in action.identified_risks
    )
    risk_normalized = _normalize(risk_texts)

    if any(ref in risk_normalized for ref in target_refs):
        clause_score = 0.30
        feedback_parts.append("✓ Correctly identified Section 7 (Limitation of Liability).")
    elif any(ref in normalized_all for ref in target_refs):
        clause_score = 0.20
        feedback_parts.append("~ Mentioned Section 7 but not as a structured identified risk.")
    elif _text_contains_any(normalized_all, ["liability", "limitation"]):
        clause_score = 0.10
        feedback_parts.append("~ Mentioned liability generally but did not pinpoint Section 7.")
    else:
        feedback_parts.append("✗ Did not identify Section 7 (Limitation of Liability).")

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
        feedback_parts.append("✓ Correctly classified the risk as one-sided/unfair.")
    elif matches >= 2:
        risk_score = 0.18
        feedback_parts.append("~ Partially classified the risk type.")
    elif matches >= 1:
        risk_score = 0.10
        feedback_parts.append("~ Vaguely identified risk type.")
    else:
        feedback_parts.append("✗ Did not classify the risk type correctly.")

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
    if exp_matches >= 4:
        explanation_score = 0.25
        feedback_parts.append("✓ Excellent explanation of why the clause is problematic.")
    elif exp_matches >= 3:
        explanation_score = 0.20
        feedback_parts.append("~ Good explanation with some key points.")
    elif exp_matches >= 2:
        explanation_score = 0.15
        feedback_parts.append("~ Partial explanation.")
    elif exp_matches >= 1:
        explanation_score = 0.08
        feedback_parts.append("~ Minimal explanation provided.")
    else:
        feedback_parts.append("✗ No substantive explanation of the risk.")

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

    if has_recs and rec_matches >= 2:
        rec_score = 0.20
        feedback_parts.append("✓ Provided actionable recommendations.")
    elif has_recs or rec_matches >= 2:
        rec_score = 0.12
        feedback_parts.append("~ Some recommendations but could be more specific.")
    elif rec_matches >= 1:
        rec_score = 0.06
        feedback_parts.append("~ Minimal recommendation provided.")
    else:
        feedback_parts.append("✗ No recommendations for remediation.")

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
            score = max(0.0, score - penalty)
            feedback_parts.append(
                f"⚠ Penalty: Multiple incorrect clause references ({len(wrong_sections)} irrelevant sections flagged)."
            )

    # =============================================================================
    # ADVANCED EVALUATION ADJUSTMENTS (ADD THIS BLOCK)
    # =============================================================================

    # 1. Overconfidence / verbosity penalty
    word_count = len(_normalize(all_text).split())
    if word_count > 600:
        penalty = min(0.05, score * 0.1)
        score -= penalty
        feedback_parts.append("⚠ Penalty: Overly verbose response reduces clarity.")

    # 2. False positive penalty (too many risks = low precision)
    if len(action.identified_risks) > 5:
        penalty = min(0.08, score * 0.12)
        score -= penalty
        feedback_parts.append("⚠ Penalty: Too many risks identified (possible false positives).")

    # 3. Missing section reference penalty (lack of grounding)
    if "section" not in _normalize(all_text):
        penalty = min(0.05, score * 0.1)
        score -= penalty
        feedback_parts.append("⚠ Penalty: No specific clause references provided.")

    # 4. Structured output bonus (good format)
    if isinstance(action.identified_risks, list) and len(action.identified_risks) > 0:
        score += 0.03
        feedback_parts.append("✓ Bonus: Proper structured output format.")

    # 5. Cross-clause reasoning bonus (advanced thinking)
    # Applied only in grade_hard

    # Clamp final score safely
    score = round(min(1.0, max(0.0, score)), 4)
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

    # --- 1. Missing Clause Identification (0.35) ---
    missing_score = 0.0
    indemnify_keywords = [
        "indemnif", "indemnity", "indemnification", "indemnities",
        "hold harmless", "defend and hold",
    ]

    # Check the missing_clauses field specifically
    missing_texts = " ".join(
        " ".join(m.values()) for m in action.missing_clauses
    )
    missing_normalized = _normalize(missing_texts)

    found_in_missing = any(kw in missing_normalized for kw in indemnify_keywords)
    found_anywhere = any(kw in normalized_all for kw in indemnify_keywords)

    if found_in_missing:
        missing_score = 0.35
        feedback_parts.append("✓ Correctly identified indemnification as a missing clause.")
    elif found_anywhere:
        missing_score = 0.22
        feedback_parts.append("~ Mentioned indemnification but not as a structured missing clause.")
    elif len(action.missing_clauses) > 0:
        # Agent identified something is missing but not indemnification
        missing_score = 0.10
        feedback_parts.append("~ Identified missing clauses but not indemnification specifically.")
    else:
        # Check if they mentioned anything about missing protections
        missing_general = ["missing", "absent", "omit", "lacks", "no provision", "not included", "not present", "does not contain", "does not include"]
        if any(kw in normalized_all for kw in missing_general):
            missing_score = 0.08
            feedback_parts.append("~ Noted missing elements generally but didn't identify indemnification.")
        else:
            feedback_parts.append("✗ Did not identify any missing clauses.")

    score += missing_score

    # --- 2. Specificity (0.25) ---
    specificity_score = 0.0
    specific_keywords = [
        "third-party claim", "third party claim", "third-party",
        "ip infringement", "intellectual property",
        "data breach", "breach damages",
        "subcontractor", "sub-contractor",
        "defense obligation", "defend",
    ]

    spec_matches = _count_keyword_matches(normalized_all, specific_keywords)
    if spec_matches >= 3:
        specificity_score = 0.25
        feedback_parts.append("✓ Detailed analysis of specific indemnification scenarios.")
    elif spec_matches >= 2:
        specificity_score = 0.18
        feedback_parts.append("~ Good specificity in indemnification analysis.")
    elif spec_matches >= 1:
        specificity_score = 0.10
        feedback_parts.append("~ Some specific context provided.")
    elif found_anywhere:
        specificity_score = 0.05
        feedback_parts.append("~ Mentioned indemnification but lacked specifics.")
    else:
        feedback_parts.append("✗ No specific indemnification context.")

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
    if imp_matches >= 3:
        importance_score = 0.20
        feedback_parts.append("✓ Well-explained importance of indemnification.")
    elif imp_matches >= 2:
        importance_score = 0.14
        feedback_parts.append("~ Adequately explained importance.")
    elif imp_matches >= 1:
        importance_score = 0.07
        feedback_parts.append("~ Briefly noted importance.")
    else:
        feedback_parts.append("✗ Did not explain importance of the missing clause.")

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

    if has_recs and sugg_matches >= 3:
        suggested_score = 0.20
        feedback_parts.append("✓ Provided specific indemnification clause recommendations.")
    elif has_recs and sugg_matches >= 1:
        suggested_score = 0.14
        feedback_parts.append("~ Good recommendations with some specificity.")
    elif has_recs or sugg_matches >= 2:
        suggested_score = 0.08
        feedback_parts.append("~ Some recommendations provided.")
    elif sugg_matches >= 1:
        suggested_score = 0.04
        feedback_parts.append("~ Minimal suggestion.")
    else:
        feedback_parts.append("✗ No suggestions for adding indemnification.")

    score += suggested_score

    # =============================================================================
    # ADVANCED EVALUATION ADJUSTMENTS (ADD THIS BLOCK)
    # =============================================================================

    # 1. Overconfidence / verbosity penalty
    word_count = len(_normalize(all_text).split())
    if word_count > 250:
        penalty = min(0.05, score * 0.1)
        score -= penalty
        feedback_parts.append("⚠ Penalty: Overly verbose response reduces clarity.")

    # 2. False positive penalty (too many risks = low precision)
    if len(action.identified_risks) > 5:
        penalty = min(0.08, score * 0.12)
        score -= penalty
        feedback_parts.append("⚠ Penalty: Too many risks identified (possible false positives).")

    # 3. Missing section reference penalty (lack of grounding)
    if "section" not in _normalize(all_text):
        penalty = min(0.05, score * 0.1)
        score -= penalty
        feedback_parts.append("⚠ Penalty: No specific clause references provided.")

    # 4. Structured output bonus (good format)
    if isinstance(action.identified_risks, list) and len(action.identified_risks) > 0:
        score += 0.03
        feedback_parts.append("✓ Bonus: Proper structured output format.")

    # 5. Cross-clause reasoning bonus (advanced thinking)
    if action.contradictions and len(action.contradictions) > 0:
        score += min(0.05, 1.0 - score)
        feedback_parts.append("✓ Bonus: Identified cross-clause reasoning.")

    # Clamp final score safely
    score = round(min(1.0, max(0.0, score)), 4)
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

    has_section_4_in_contradictions = _has_section_ref(contradiction_texts, "4")
    has_section_11_in_contradictions = _has_section_ref(contradiction_texts, "11")
    has_section_4_anywhere = _has_section_ref(all_text, "4")
    has_section_11_anywhere = _has_section_ref(all_text, "11")
    has_section_10_anywhere = _has_section_ref(all_text, "10")

    # --- 1. Primary Contradiction Found (0.30) ---
    primary_score = 0.0
    warranty_keywords = ["warranty", "warranties", "performance guarantee", "guarantee"]
    liability_keywords = ["limitation of liability", "liability cap", "liability limit", "damages cap"]

    both_in_contradictions = has_section_4_in_contradictions and has_section_11_in_contradictions
    both_anywhere = has_section_4_anywhere and has_section_11_anywhere

    # Also check for warranty vs liability language
    warranty_found = any(kw in normalized_all for kw in warranty_keywords)
    liability_found = any(kw in normalized_all for kw in liability_keywords)

    if both_in_contradictions:
        primary_score = 0.30
        feedback_parts.append("✓ Correctly identified Section 4 vs Section 11 contradiction in structured format.")
    elif both_anywhere and len(action.contradictions) > 0:
        primary_score = 0.25
        feedback_parts.append("~ Identified both sections with some contradiction analysis.")
    elif both_anywhere:
        primary_score = 0.20
        feedback_parts.append("~ Referenced both Section 4 and Section 11 but not as structured contradiction.")
    elif (has_section_4_anywhere or has_section_11_anywhere) and warranty_found and liability_found:
        primary_score = 0.15
        feedback_parts.append("~ Identified warranty vs liability tension but missing specific section pairing.")
    elif warranty_found and liability_found:
        primary_score = 0.10
        feedback_parts.append("~ Noted warranty and liability themes but didn't identify specific sections.")
    elif has_section_4_anywhere or has_section_11_anywhere:
        primary_score = 0.08
        feedback_parts.append("~ Found one of the conflicting sections but not the pairing.")
    else:
        feedback_parts.append("✗ Did not identify the primary contradiction (Section 4 vs Section 11).")

    score += primary_score

    # --- 2. Both Clauses Identified (0.20) ---
    both_score = 0.0
    if both_in_contradictions:
        both_score = 0.20
        feedback_parts.append("✓ Both contradictory clauses precisely identified.")
    elif both_anywhere:
        both_score = 0.14
        feedback_parts.append("~ Both sections mentioned but not clearly paired.")
    elif has_section_4_anywhere or has_section_11_anywhere:
        both_score = 0.07
        feedback_parts.append("~ Only one of the two contradictory sections identified.")
    else:
        feedback_parts.append("✗ Neither contradictory section specifically identified.")

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
    if exp_matches >= 5:
        explanation_score = 0.25
        feedback_parts.append("✓ Excellent explanation of how the clauses contradict each other.")
    elif exp_matches >= 4:
        explanation_score = 0.20
        feedback_parts.append("~ Strong explanation of the contradiction.")
    elif exp_matches >= 3:
        explanation_score = 0.15
        feedback_parts.append("~ Good partial explanation.")
    elif exp_matches >= 2:
        explanation_score = 0.10
        feedback_parts.append("~ Some explanation of the conflict.")
    elif exp_matches >= 1:
        explanation_score = 0.05
        feedback_parts.append("~ Minimal explanation.")
    else:
        feedback_parts.append("✗ No meaningful explanation of the contradiction.")

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
    if loop_matches >= 3:
        loophole_score = 0.15
        feedback_parts.append("✓ Identified the legal loophole and its implications.")
    elif loop_matches >= 2:
        loophole_score = 0.10
        feedback_parts.append("~ Partially identified the loophole.")
    elif loop_matches >= 1:
        loophole_score = 0.05
        feedback_parts.append("~ Vague loophole awareness.")
    else:
        feedback_parts.append("✗ Did not identify the legal loophole.")

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
            feedback_parts.append("✓ Also identified Section 10 vs 11 conflict (Maintenance SLAs vs Liability cap).")
        else:
            secondary_score = 0.05
            feedback_parts.append("~ Referenced Section 10 but without detailed conflict analysis.")
    else:
        # Check for any other valid observations
        other_valid = ["arbitrator", "punitive", "no authority", "13.3"]
        if any(kw in normalized_all for kw in other_valid):
            secondary_score = 0.05
            feedback_parts.append("~ Noted other valid contractual concerns.")
        else:
            feedback_parts.append("~ Did not identify secondary conflicts (e.g., Section 10 vs 11).")

    score += secondary_score

    # =============================================================================
    # ADVANCED EVALUATION ADJUSTMENTS (ADD THIS BLOCK)
    # =============================================================================

    # 1. Overconfidence / verbosity penalty
    word_count = len(_normalize(all_text).split())
    if word_count > 250:
        penalty = min(0.05, score * 0.1)
        score -= penalty
        feedback_parts.append("⚠ Penalty: Overly verbose response reduces clarity.")

    # 2. False positive penalty (too many risks = low precision)
    if len(action.identified_risks) > 5:
        penalty = min(0.08, score * 0.12)
        score -= penalty
        feedback_parts.append("⚠ Penalty: Too many risks identified (possible false positives).")

    # 3. Missing section reference penalty (lack of grounding)
    if "section" not in _normalize(all_text):
        penalty = min(0.05, score * 0.1)
        score -= penalty
        feedback_parts.append("⚠ Penalty: No specific clause references provided.")

    # 4. Structured output bonus (good format)
    if isinstance(action.identified_risks, list) and len(action.identified_risks) > 0:
        score += 0.03
        feedback_parts.append("✓ Bonus: Proper structured output format.")

    # 5. Cross-clause reasoning bonus (advanced thinking)
    if action.contradictions and len(action.contradictions) > 0:
        score += min(0.05, 1.0 - score)
        feedback_parts.append("✓ Bonus: Identified cross-clause reasoning.")

    # Clamp final score safely
    score = round(min(1.0, max(0.0, score)), 4)
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
        return 0.0, f"Unknown task_id: {task_id}"
    return GRADERS[task_id](action)

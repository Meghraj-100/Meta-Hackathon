"""
Contract data and ground truth for the Legal Contract Risk Reviewer.

Contains 3 realistic contract scenarios with embedded legal issues:
- Task 1 (Easy): One-sided liability clause
- Task 2 (Medium): Missing indemnification clause
- Task 3 (Hard): Contradictory clauses creating a legal loophole
"""

from typing import Any, Dict, List


# =============================================================================
# TASK 1 — EASY: One-Sided Liability Clause
# =============================================================================

TASK_1_CONTRACT = """
SOFTWARE SERVICES AGREEMENT

This Software Services Agreement ("Agreement") is entered into as of January 15, 2025,
by and between TechVendor Solutions Inc. ("Provider") and Acme Corporation ("Client").

SECTION 1: SCOPE OF SERVICES
1.1 Provider shall deliver cloud-based enterprise resource planning (ERP) software
    services as described in Exhibit A ("Services").
1.2 Services shall include implementation, configuration, data migration, and
    ongoing technical support.
1.3 Provider shall assign a dedicated project manager to oversee delivery.

SECTION 2: TERM AND TERMINATION
2.1 This Agreement shall commence on the Effective Date and continue for a period
    of thirty-six (36) months ("Initial Term").
2.2 Either party may terminate this Agreement for cause upon sixty (60) days written
    notice if the other party materially breaches this Agreement and fails to cure
    such breach within the notice period.
2.3 Client may terminate for convenience upon ninety (90) days written notice,
    subject to payment of early termination fees as specified in Exhibit B.

SECTION 3: FEES AND PAYMENT
3.1 Client shall pay Provider the fees set forth in Exhibit B.
3.2 All invoices are due within thirty (30) days of receipt.
3.3 Late payments shall accrue interest at the rate of 1.5% per month.

SECTION 4: INTELLECTUAL PROPERTY
4.1 Provider retains all intellectual property rights in the Services and any
    pre-existing materials.
4.2 Client retains all rights in Client Data uploaded to the platform.
4.3 Any customizations developed specifically for Client shall be jointly owned.

SECTION 5: DATA PROTECTION
5.1 Provider shall implement industry-standard security measures to protect Client Data.
5.2 Provider shall comply with applicable data protection regulations.
5.3 Upon termination, Provider shall return or destroy Client Data within thirty (30) days.

SECTION 6: CONFIDENTIALITY
6.1 Each party shall maintain the confidentiality of the other party's Confidential
    Information for a period of five (5) years following disclosure.
6.2 Confidential Information excludes information that is publicly available or
    independently developed.

SECTION 7: LIMITATION OF LIABILITY
7.1 UNDER NO CIRCUMSTANCES SHALL PROVIDER BE LIABLE TO CLIENT FOR ANY DIRECT,
    INDIRECT, INCIDENTAL, CONSEQUENTIAL, SPECIAL, PUNITIVE, OR EXEMPLARY DAMAGES
    ARISING OUT OF OR RELATED TO THIS AGREEMENT, INCLUDING BUT NOT LIMITED TO
    DAMAGES FOR LOSS OF PROFITS, LOSS OF DATA, BUSINESS INTERRUPTION, OR ANY
    OTHER COMMERCIAL DAMAGES OR LOSSES, REGARDLESS OF THE CAUSE OF ACTION OR
    THE THEORY OF LIABILITY, EVEN IF PROVIDER HAS BEEN ADVISED OF THE POSSIBILITY
    OF SUCH DAMAGES. THIS LIMITATION APPLIES TO ALL CLAIMS INCLUDING THOSE
    ARISING FROM PROVIDER'S GROSS NEGLIGENCE, WILLFUL MISCONDUCT, OR FRAUD.
7.2 Client's sole and exclusive remedy for any claim arising under this Agreement
    shall be limited to discontinuation of the Services.
7.3 Client agrees to bear all risks associated with the use of the Services,
    including any damages to Client's systems, data loss, or business disruption.

SECTION 8: WARRANTIES
8.1 Provider warrants that the Services shall perform substantially in accordance
    with the documentation for a period of ninety (90) days from delivery.
8.2 EXCEPT AS SET FORTH IN SECTION 8.1, PROVIDER MAKES NO WARRANTIES, EXPRESS OR
    IMPLIED, INCLUDING WARRANTIES OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.

SECTION 9: GOVERNING LAW
9.1 This Agreement shall be governed by the laws of the State of Delaware.
9.2 Any disputes shall be resolved through binding arbitration in Wilmington, Delaware.

SECTION 10: GENERAL PROVISIONS
10.1 This Agreement constitutes the entire agreement between the parties.
10.2 This Agreement may not be amended except in writing signed by both parties.
10.3 If any provision is found unenforceable, the remaining provisions shall remain in effect.
"""

TASK_1_GROUND_TRUTH = {
    "task_id": "task_1_easy",
    "difficulty": "easy",
    "description": "Identify the one-sided liability clause in this vendor agreement.",
    "instructions": (
        "You are a legal contract risk reviewer. Analyze the following software services "
        "agreement and identify any risky, one-sided, or unfair clauses. Pay special "
        "attention to liability limitations and risk allocation between the parties. "
        "Provide your analysis as a structured response identifying risks, explaining "
        "why they are problematic, and recommending changes."
    ),
    "target_clauses": ["Section 7", "7.1", "7.2", "7.3"],
    "risk_types": ["one-sided liability", "liability exclusion", "unfair limitation", "unconscionable"],
    "key_issues": [
        "provider excludes all liability including gross negligence and fraud",
        "client bears all risk",
        "no cap on liability - complete exclusion",
        "sole remedy is discontinuation only",
        "waives consequential damages entirely",
        "covers willful misconduct and fraud which is unusual and likely unenforceable",
    ],
    "expected_recommendations": [
        "add mutual liability provisions",
        "cap liability at contract value or fees paid",
        "exclude gross negligence and fraud from limitation",
        "allow monetary damages as remedy",
        "negotiate balanced risk allocation",
    ],
}


# =============================================================================
# TASK 2 — MEDIUM: Missing Indemnification Clause
# =============================================================================

TASK_2_CONTRACT = """
PROFESSIONAL CONSULTING SERVICES AGREEMENT

This Professional Consulting Services Agreement ("Agreement") is entered into as of
March 1, 2025, by and between DataWorks Analytics LLC ("Consultant") and GlobalRetail
Holdings Inc. ("Client").

SECTION 1: ENGAGEMENT AND SCOPE
1.1 Client engages Consultant to provide data analytics consulting services including
    but not limited to: data warehouse design, predictive modeling, customer
    segmentation analysis, and business intelligence dashboard development ("Services").
1.2 Consultant shall provide Services in accordance with the Statement of Work
    attached as Exhibit A.
1.3 Consultant may engage subcontractors to perform portions of the Services,
    provided Consultant remains responsible for their performance.

SECTION 2: TERM
2.1 This Agreement shall be effective from the date of execution and shall continue
    for a period of twenty-four (24) months.
2.2 The Agreement may be renewed for additional twelve (12) month periods upon
    mutual written consent of both parties.

SECTION 3: COMPENSATION
3.1 Client shall pay Consultant at the rates specified in Exhibit B.
3.2 Consultant shall submit monthly invoices for Services performed.
3.3 Payment is due within forty-five (45) days of invoice date.
3.4 Client shall reimburse Consultant for pre-approved travel and out-of-pocket
    expenses within thirty (30) days of submission.

SECTION 4: INTELLECTUAL PROPERTY RIGHTS
4.1 All work product, deliverables, reports, models, and analyses created by
    Consultant in performing the Services ("Work Product") shall be the exclusive
    property of Client upon full payment.
4.2 Consultant retains ownership of pre-existing tools, methodologies, and
    frameworks ("Consultant IP") used in performing the Services.
4.3 Consultant grants Client a non-exclusive, perpetual, royalty-free license to
    use Consultant IP as embedded in the Work Product.
4.4 Client grants Consultant a limited license to use Client Data solely for
    performing the Services.

SECTION 5: CONFIDENTIALITY
5.1 Each party agrees to hold in confidence all Confidential Information received
    from the other party.
5.2 Confidential Information means any non-public information disclosed by either
    party, including business plans, financial data, customer information, trade
    secrets, and technical data.
5.3 Confidentiality obligations shall survive termination for three (3) years.
5.4 Confidential Information does not include information that: (a) is or becomes
    publicly available through no fault of the receiving party; (b) was known to
    the receiving party prior to disclosure; (c) is independently developed; or
    (d) is disclosed pursuant to legal requirement.

SECTION 6: DATA HANDLING AND PRIVACY
6.1 Consultant shall handle all Client Data in compliance with applicable data
    protection laws including GDPR, CCPA, and other relevant regulations.
6.2 Consultant shall implement appropriate technical and organizational security
    measures to protect Client Data.
6.3 Consultant shall notify Client within seventy-two (72) hours of discovering
    any data breach affecting Client Data.
6.4 Upon project completion or termination, Consultant shall securely delete or
    return all Client Data within fifteen (15) business days.

SECTION 7: REPRESENTATIONS AND WARRANTIES
7.1 Consultant represents and warrants that: (a) it has the expertise and
    qualifications to perform the Services; (b) Services will be performed in a
    professional manner consistent with industry standards; (c) the Work Product
    will not infringe any third-party intellectual property rights.
7.2 Client represents and warrants that: (a) it has the authority to enter into
    this Agreement; (b) Client Data provided to Consultant has been collected in
    compliance with applicable laws.

SECTION 8: LIMITATION OF LIABILITY
8.1 Neither party shall be liable for indirect, incidental, or consequential
    damages arising from this Agreement.
8.2 Each party's total aggregate liability under this Agreement shall not exceed
    the total fees paid or payable under this Agreement during the twelve (12)
    months preceding the claim.
8.3 The limitations in this Section 8 shall not apply to breaches of
    confidentiality obligations or intellectual property infringement.

SECTION 9: TERMINATION
9.1 Either party may terminate this Agreement for cause if the other party
    materially breaches and fails to cure within thirty (30) days of written notice.
9.2 Either party may terminate for convenience upon sixty (60) days written notice.
9.3 Upon termination, Client shall pay for all Services rendered through the
    effective date of termination.
9.4 Sections 4, 5, 6, 7, 8, and 10 shall survive termination.

SECTION 10: DISPUTE RESOLUTION
10.1 The parties shall first attempt to resolve disputes through good-faith
     negotiation for thirty (30) days.
10.2 If negotiation fails, disputes shall be submitted to mediation.
10.3 If mediation is unsuccessful, disputes shall be resolved by binding
     arbitration under the rules of the American Arbitration Association.
10.4 The prevailing party shall be entitled to recover reasonable attorneys' fees.

SECTION 11: GENERAL PROVISIONS
11.1 This Agreement shall be governed by the laws of the State of New York.
11.2 This Agreement constitutes the entire agreement between the parties.
11.3 Neither party may assign this Agreement without prior written consent.
11.4 Any waiver must be in writing and signed by the waiving party.
11.5 If any provision is held invalid, the remaining provisions remain in effect.
11.6 This Agreement may be executed in counterparts.
"""

TASK_2_GROUND_TRUTH = {
    "task_id": "task_2_medium",
    "difficulty": "medium",
    "description": "Identify the missing indemnification clause in this consulting agreement.",
    "instructions": (
        "You are a legal contract risk reviewer. Analyze the following professional "
        "consulting services agreement thoroughly. Your task is to identify any missing "
        "standard legal protections that should be present in a contract of this nature. "
        "Consider what clauses are typically included in professional services agreements "
        "and identify any significant omissions. Provide your analysis as a structured "
        "response listing missing clauses, their importance, and suggested language."
    ),
    "missing_clause_types": [
        "indemnification",
        "indemnity",
        "hold harmless",
    ],
    "key_issues": [
        "no indemnification clause exists in the agreement",
        "neither party is required to indemnify the other",
        "no protection against third-party claims",
        "ip infringement warranty exists but no indemnification backing it",
        "data breach notification exists but no indemnification for breach damages",
        "subcontractor use allowed but no indemnification for subcontractor actions",
    ],
    "expected_recommendations": [
        "add mutual indemnification clause",
        "consultant should indemnify for ip infringement",
        "consultant should indemnify for data breaches caused by consultant",
        "consultant should indemnify for subcontractor actions",
        "client should indemnify for claims arising from client data",
        "include defense and hold harmless obligations",
        "specify indemnification procedures and notice requirements",
    ],
    "sections_present": [
        "scope", "term", "compensation", "ip", "confidentiality",
        "data handling", "warranties", "limitation of liability",
        "termination", "dispute resolution", "general provisions",
    ],
}


# =============================================================================
# TASK 3 — HARD: Contradictory Clauses Creating a Legal Loophole
# =============================================================================

TASK_3_CONTRACT = """
ENTERPRISE SOFTWARE LICENSE AND MAINTENANCE AGREEMENT

This Enterprise Software License and Maintenance Agreement ("Agreement") is entered
into as of February 1, 2025, by and between NexGen Software Corp. ("Licensor") and
Pacific Manufacturing Group Inc. ("Licensee").

SECTION 1: DEFINITIONS
1.1 "Software" means the NexGen Enterprise Manufacturing Suite version 5.0, including
    all modules, components, and associated documentation.
1.2 "Maintenance Services" means bug fixes, patches, updates, and technical support
    as described in Section 10.
1.3 "Defect" means any failure of the Software to conform to the specifications set
    forth in the Documentation.
1.4 "Critical Defect" means a Defect that renders a core function of the Software
    inoperable or causes data corruption.
1.5 "Service Level Agreement" or "SLA" means the performance standards and remedies
    set forth in Exhibit C.

SECTION 2: LICENSE GRANT
2.1 Licensor grants Licensee a non-exclusive, non-transferable license to use the
    Software for Licensee's internal business operations.
2.2 The license covers up to five hundred (500) named users across Licensee's
    facilities in North America.
2.3 Licensee may not sublicense, rent, lease, or distribute the Software.

SECTION 3: LICENSE FEES AND PAYMENT
3.1 Licensee shall pay the license fee of $2,400,000 as specified in Exhibit B.
3.2 Annual maintenance fees of $480,000 shall be payable in advance on each
    anniversary of the Effective Date.
3.3 Payment terms are net thirty (30) days from invoice date.
3.4 Licensor reserves the right to suspend access to the Software if any payment
    is more than sixty (60) days overdue.

SECTION 4: SOFTWARE WARRANTY AND PERFORMANCE GUARANTEE
4.1 Licensor warrants and guarantees that the Software shall perform in strict
    conformity with all specifications and functions described in the Documentation
    for the entire duration of this Agreement ("Performance Guarantee").
4.2 Licensor further warrants that the Software shall maintain an uptime of
    99.9% measured monthly, excluding scheduled maintenance windows.
4.3 In the event the Software fails to meet the Performance Guarantee, Licensor
    shall, AT LICENSOR'S EXPENSE AND OBLIGATION:
    (a) promptly diagnose and repair any Defects;
    (b) provide temporary workarounds within four (4) hours for Critical Defects;
    (c) deliver permanent fixes within five (5) business days for Critical Defects;
    (d) credit Licensee for any periods of non-conformance pro-rata against the
        annual maintenance fee.
4.4 Licensor warrants that the Software does not infringe any third-party
    intellectual property rights as of the Effective Date.
4.5 Licensor warrants that it has the full right, power, and authority to grant
    the license and perform its obligations under this Agreement.
4.6 THE WARRANTIES IN THIS SECTION 4 ARE COMPREHENSIVE AND REPRESENT LICENSOR'S
    COMPLETE WARRANTY OBLIGATIONS. Licensor stands behind these warranties fully
    and commits to their enforcement throughout the Agreement term.

SECTION 5: IMPLEMENTATION AND ACCEPTANCE
5.1 Licensor shall implement the Software in accordance with the project plan
    in Exhibit D.
5.2 Upon completion of implementation, Licensee shall have thirty (30) days to
    conduct acceptance testing.
5.3 If the Software fails acceptance testing, Licensor shall correct all identified
    issues within fifteen (15) business days, and Licensee shall have an additional
    fifteen (15) days for re-testing.

SECTION 6: INTELLECTUAL PROPERTY
6.1 Licensor retains all right, title, and interest in the Software and all
    related intellectual property.
6.2 Licensee retains ownership of all data entered into or generated by the Software.
6.3 Any modifications or customizations to the Software shall be owned by Licensor.

SECTION 7: CONFIDENTIALITY
7.1 Each party shall maintain the confidentiality of the other party's proprietary
    information for the duration of this Agreement and three (3) years thereafter.
7.2 Confidential Information includes source code, business processes, customer
    data, and financial information.

SECTION 8: DATA SECURITY
8.1 Licensor shall implement enterprise-grade security measures to protect
    Licensee's data, including encryption at rest and in transit.
8.2 Licensor shall comply with SOC 2 Type II certification requirements.
8.3 Licensor shall promptly notify Licensee of any security incident.
8.4 Licensor shall conduct annual penetration testing and share results with Licensee.

SECTION 9: INDEMNIFICATION
9.1 Licensor shall indemnify, defend, and hold harmless Licensee from and against
    any claims arising from: (a) infringement of third-party intellectual property
    rights by the Software; (b) Licensor's breach of its confidentiality obligations;
    (c) Licensor's gross negligence or willful misconduct.
9.2 Licensee shall indemnify, defend, and hold harmless Licensor from and against
    any claims arising from: (a) Licensee's use of the Software in violation of this
    Agreement; (b) Licensee's data or content that infringes third-party rights.
9.3 The indemnifying party shall have sole control of the defense and settlement
    of any indemnified claim.

SECTION 10: MAINTENANCE AND SUPPORT
10.1 Licensor shall provide Maintenance Services during the term of this Agreement.
10.2 Maintenance Services include: (a) telephone and email support during business
     hours (8 AM - 6 PM EST, Mon-Fri); (b) 24/7 emergency support for Critical
     Defects; (c) software updates and patches; (d) access to online knowledge base.
10.3 Licensor shall maintain response times as follows:
     - Critical Defects: 1 hour response, 4 hour workaround
     - Major Defects: 4 hour response, 2 business day resolution
     - Minor Defects: 1 business day response, 5 business day resolution

SECTION 11: LIMITATION OF LIABILITY
11.1 NOTWITHSTANDING ANY OTHER PROVISION OF THIS AGREEMENT, INCLUDING BUT NOT
     LIMITED TO THE WARRANTIES SET FORTH IN SECTION 4 AND THE MAINTENANCE
     OBLIGATIONS IN SECTION 10, LICENSOR'S TOTAL AGGREGATE LIABILITY ARISING
     OUT OF OR RELATED TO THIS AGREEMENT SHALL NOT EXCEED THE LESSER OF:
     (A) THE FEES ACTUALLY PAID BY LICENSEE IN THE SIX (6) MONTHS PRECEDING
     THE CLAIM, OR (B) TWO HUNDRED AND FORTY THOUSAND DOLLARS ($240,000).
11.2 IN NO EVENT SHALL LICENSOR BE LIABLE FOR ANY INDIRECT, INCIDENTAL,
     CONSEQUENTIAL, SPECIAL, OR PUNITIVE DAMAGES, INCLUDING BUT NOT LIMITED TO
     LOSS OF PROFITS, LOSS OF DATA, LOSS OF PRODUCTION, MANUFACTURING DELAYS,
     OR BUSINESS INTERRUPTION, REGARDLESS OF WHETHER SUCH DAMAGES WERE
     FORESEEABLE OR WHETHER LICENSOR WAS ADVISED OF THEIR POSSIBILITY.
11.3 THE LIMITATIONS IN THIS SECTION 11 SHALL APPLY TO ALL CAUSES OF ACTION
     IN THE AGGREGATE, INCLUDING BREACH OF CONTRACT, BREACH OF WARRANTY,
     NEGLIGENCE, STRICT LIABILITY, AND ANY OTHER LEGAL THEORY.
11.4 LICENSEE ACKNOWLEDGES THAT THE FEES CHARGED REFLECT THE ALLOCATION OF
     RISK SET FORTH IN THIS AGREEMENT AND THAT LICENSOR WOULD NOT ENTER INTO
     THIS AGREEMENT WITHOUT THESE LIMITATIONS.
11.5 THIS SECTION 11 SHALL PREVAIL OVER ANY CONFLICTING PROVISION IN THIS
     AGREEMENT TO THE FULLEST EXTENT PERMITTED BY APPLICABLE LAW.

SECTION 12: TERM AND TERMINATION
12.1 This Agreement shall have an initial term of five (5) years from the
     Effective Date.
12.2 Annual maintenance shall automatically renew unless either party provides
     ninety (90) days written notice of non-renewal.
12.3 Either party may terminate for material breach upon forty-five (45) days
     written notice and failure to cure.
12.4 Licensor may terminate immediately if Licensee fails to pay any fees within
     ninety (90) days of the due date.
12.5 Upon termination, Licensee shall cease all use of the Software and return
     or destroy all copies.

SECTION 13: GOVERNING LAW AND DISPUTE RESOLUTION
13.1 This Agreement shall be governed by the laws of the State of California.
13.2 All disputes shall be resolved by binding arbitration in San Francisco, CA.
13.3 The arbitrator shall have no authority to award punitive damages.
13.4 The prevailing party shall be entitled to recover reasonable attorneys' fees.

SECTION 14: GENERAL PROVISIONS
14.1 This Agreement constitutes the entire agreement between the parties.
14.2 Amendments must be in writing and signed by authorized representatives.
14.3 Neither party may assign without prior written consent.
14.4 Failure to enforce any provision shall not constitute a waiver.
14.5 If any provision is unenforceable, the remaining provisions remain in effect.
14.6 All notices shall be in writing and sent to the addresses in Exhibit A.
"""

TASK_3_GROUND_TRUTH = {
    "task_id": "task_3_hard",
    "difficulty": "hard",
    "description": (
        "Detect contradictions between clauses in this long enterprise software "
        "agreement that create legal loopholes."
    ),
    "instructions": (
        "You are an expert legal contract risk reviewer. Carefully analyze the following "
        "enterprise software license and maintenance agreement. This is a complex contract "
        "with multiple interrelated provisions. Your task is to identify any CONTRADICTIONS "
        "between different sections of the contract that could create legal loopholes or "
        "render certain protections unenforceable. Pay close attention to how warranty "
        "provisions, liability limitations, and remedy clauses interact. Consider whether "
        "the promises made in one section are effectively nullified by provisions in another. "
        "Provide a detailed analysis of any contradictions found, explaining the specific "
        "conflict and the legal risk it creates."
    ),
    "contradictory_pairs": [
        {
            "clause_a": "Section 4",
            "clause_a_label": "Software Warranty and Performance Guarantee",
            "clause_b": "Section 11",
            "clause_b_label": "Limitation of Liability",
            "explanation": (
                "Section 4 provides comprehensive warranties including a performance guarantee, "
                "99.9% uptime commitment, obligation to fix defects at Licensor's expense, "
                "and pro-rata credits. However, Section 11 caps total liability at only "
                "$240,000 (6 months of maintenance fees) and excludes ALL consequential "
                "damages including loss of production and manufacturing delays. This means "
                "the warranty promises in Section 4 are effectively hollow — if the software "
                "fails catastrophically, the maximum recovery is $240,000 on a $2.4M+ contract. "
                "Section 11.5 explicitly states it prevails over conflicting provisions."
            ),
        },
        {
            "clause_a": "Section 4",
            "clause_a_label": "Software Warranty and Performance Guarantee",
            "clause_b": "Section 11",
            "clause_b_label": "Limitation of Liability",
            "explanation": (
                "Section 4.3 promises repair obligations 'at Licensor's expense' with specific "
                "SLAs (4-hour workaround, 5-day fix for Critical Defects), but Section 11.3 "
                "applies liability caps to 'breach of warranty' claims. If Licensor fails to "
                "meet its warranty obligations and causes $5M in manufacturing downtime, the "
                "Licensee can only recover $240K. The warranty creates an expectation of "
                "reliability that the liability cap completely undermines."
            ),
        },
        {
            "clause_a": "Section 10",
            "clause_a_label": "Maintenance and Support SLAs",
            "clause_b": "Section 11",
            "clause_b_label": "Limitation of Liability",
            "explanation": (
                "Section 10 defines strict maintenance SLAs with specific response/resolution "
                "times (1hr/4hr for Critical). Section 11 excludes liability for 'loss of "
                "production, manufacturing delays, or business interruption' — which are "
                "exactly the damages that would result from Licensor failing to meet Section "
                "10's SLAs. The SLAs are contractual obligations with no meaningful remedy."
            ),
        },
    ],
    "key_issues": [
        "section 4 warranty contradicts section 11 liability cap",
        "performance guarantee is rendered meaningless by liability limitation",
        "section 11.5 explicitly overrides section 4 warranties",
        "consequential damages exclusion nullifies warranty remedies",
        "$240k cap on $2.4m contract creates disproportionate risk",
        "maintenance SLA obligations have no enforceable remedy",
        "section 4.6 says warranties are comprehensive but section 11 guts them",
        "loophole: licensor can breach warranties with minimal financial consequence",
    ],
    "loophole_explanation": (
        "The core loophole is that Licensor can make extensive warranty promises (Section 4) "
        "and maintenance commitments (Section 10) knowing that Section 11 limits any actual "
        "liability to a fraction of the contract value. Section 11.5 cements this by declaring "
        "that the liability section prevails over all conflicting provisions. A Licensee relying "
        "on the warranty promises would be severely under-protected. This creates a pattern "
        "where the agreement appears balanced on the surface but the liability provisions "
        "systematically strip away the protections that earlier sections promise."
    ),
    "target_sections": {
        "primary": ["Section 4", "Section 11"],
        "secondary": ["Section 10"],
    },
}


# =============================================================================
# Task Registry
# =============================================================================

TASKS = {
    "task_1_easy": {
        "contract": TASK_1_CONTRACT,
        "ground_truth": TASK_1_GROUND_TRUTH,
    },
    "task_2_medium": {
        "contract": TASK_2_CONTRACT,
        "ground_truth": TASK_2_GROUND_TRUTH,
    },
    "task_3_hard": {
        "contract": TASK_3_CONTRACT,
        "ground_truth": TASK_3_GROUND_TRUTH,
    },
}


def get_task(task_id: str) -> Dict[str, Any]:
    """Get a task by ID. Raises KeyError if not found."""
    if task_id not in TASKS:
        raise KeyError(
            f"Unknown task_id: {task_id}. Available tasks: {list(TASKS.keys())}"
        )
    return TASKS[task_id]


def get_all_task_ids() -> List[str]:
    """Return all available task IDs."""
    return list(TASKS.keys())

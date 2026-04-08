# 🧾 Aryan's Contributions — Legal Contract Risk Reviewer

## Overview

This document summarizes the work done by **Aryan Kumar** as part of the Meta Hackathon on the [Legal Contract Risk Reviewer](./README.md) project — an OpenEnv environment where AI agents analyze legal contracts to identify risky terms, missing clauses, and logical loopholes.

---

## 🔧 What I Built

### 1. Invoice Risk Review — New Task Type

Extended the environment with a fourth task: **invoice-based contract risk analysis**. Unlike the original tasks that focused on service agreements and consulting contracts, this task challenges the agent to identify financial risks embedded in invoice documents (e.g., ambiguous payment terms, missing dispute resolution clauses, unilateral late-fee provisions).

### 2. Deterministic Grading Function

Implemented a fully rule-based grader for the invoice task (`graders.py`) that scores agent responses on a **0.0 – 1.0 scale** with partial credit across four dimensions:

| Dimension | Weight |
|---|---|
| Clause Identification | ~30% |
| Risk Classification | ~25% |
| Explanation Quality | ~25% |
| Recommendations | ~20% |

The grader is deterministic — identical inputs always yield identical scores, with no LLM-as-judge variability.

### 3. Inference Script Updates

Updated `inference.py` to:
- Include the invoice task alongside the three original tasks.
- Support a **`--local-test` mode** for offline verification without a running server, using mocked environment responses.

### 4. Isolated Feature Branch

All changes were developed and tested on the `aryan` branch, keeping the `main` branch clean and unmodified throughout the hackathon.

---

## ✅ Verification

The invoice task was verified end-to-end by running `inference.py` in local test mode. The agent correctly identified key financial risks in the invoice contract and achieved a passing score above the `0.30` success threshold.

---

## 🗂️ Files Modified / Added

| File | Change |
|---|---|
| `server/contracts.py` | Added invoice contract data and ground truth |
| `server/graders.py` | Added `grade_invoice_task()` grading function |
| `server/contract_environment.py` | Registered the new invoice task |
| `inference.py` | Added invoice task to `TASKS` list; added local test mode |

---

*Branch: `aryan` | Hackathon: Meta OpenEnv Round 1 Bootcamp*
#!/usr/bin/env python3
"""
Combine individual exam JSON files into complete exam sets.
Also builds the final HTML simulator with all questions embedded.

Usage:
    python3 combine_exams.py

This script:
1. Combines all question batch files into complete exam files
2. Builds a master JSON with all exams for both AZ-900 and MS-102
3. Generates the final single-file HTML simulator
"""

import json
import os
import glob
from datetime import datetime, timezone

QUESTIONS_DIR = "questions"
OUTPUT_DIR = "."

def combine_exam_batches(cert, exam_num):
    """Combine individual batch files into a complete exam JSON."""
    pattern = os.path.join(QUESTIONS_DIR, f"{cert}_exam{exam_num}_q*.json")
    batch_files = sorted(glob.glob(pattern))

    if not batch_files:
        print(f"  WARNING: No batch files found for {cert} exam {exam_num}")
        return []

    all_questions = []
    for f in batch_files:
        with open(f) as fh:
            questions = json.load(fh)
            all_questions.extend(questions)
            print(f"  Loaded {len(questions)} questions from {os.path.basename(f)}")

    # Write complete exam file
    complete_file = os.path.join(QUESTIONS_DIR, f"{cert}_exam{exam_num}_complete.json")
    with open(complete_file, 'w') as fh:
        json.dump(all_questions, fh, indent=2)
    print(f"  => {cert}_exam{exam_num}_complete.json: {len(all_questions)} questions")

    return all_questions


def build_master_json():
    """Build the master JSON structure with all exams for both certificates."""

    master = {
        "meta": {
            "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "note": "Original practice questions aligned to public exam objectives. Not official Microsoft exam questions; no copyrighted exam items included."
        },
        "exams": [
            {
                "code": "AZ900",
                "name": "AZ-900: Microsoft Azure Fundamentals",
                "pass_scaled": 700,
                "max_scaled": 1000,
                "domains": [
                    {"name": "Cloud Concepts", "count": 15},
                    {"name": "Azure Architecture", "count": 18},
                    {"name": "Azure Management and Governance", "count": 17}
                ]
            },
            {
                "code": "MS102",
                "name": "MS-102: Microsoft 365 Endpoint Administrator",
                "pass_scaled": 700,
                "max_scaled": 1000,
                "domains": [
                    {"name": "Deploy and manage endpoints", "count": 20},
                    {"name": "Implement security and compliance", "count": 18},
                    {"name": "Manage applications", "count": 12}
                ]
            }
        ],
        "practice_sets": {
            "AZ900": [],
            "MS102": []
        }
    }

    for cert_code, cert_key in [("az900", "AZ900"), ("ms102", "MS102")]:
        print(f"\n=== {cert_key} ===")
        for exam_num in range(1, 6):
            print(f"\nExam {exam_num}:")

            # Try complete file first
            complete_file = os.path.join(QUESTIONS_DIR, f"{cert_code}_exam{exam_num}_complete.json")
            if os.path.exists(complete_file):
                with open(complete_file) as fh:
                    questions = json.load(fh)
                print(f"  Loaded {len(questions)} questions from complete file")
            else:
                # Build from batches
                questions = combine_exam_batches(cert_code, exam_num)

            if questions:
                exam_set = {
                    "set": exam_num,
                    "title": f"Practice Exam {exam_num}",
                    "questions": questions
                }
                master["practice_sets"][cert_key].append(exam_set)
                print(f"  Added to master: {len(questions)} questions")

    # Write master JSON
    master_file = os.path.join(QUESTIONS_DIR, "all_exams_master.json")
    with open(master_file, 'w') as fh:
        json.dump(master, fh, indent=2)

    # Also write compact version for HTML embedding
    compact_file = os.path.join(QUESTIONS_DIR, "all_exams_compact.json")
    with open(compact_file, 'w') as fh:
        json.dump(master, fh, separators=(',', ':'))

    compact_size = os.path.getsize(compact_file)
    print(f"\n=== MASTER JSON ===")
    print(f"  Master file: {master_file}")
    print(f"  Compact file: {compact_file} ({compact_size:,} bytes / {compact_size/1024:.0f} KB)")

    # Summary
    total = 0
    for cert_key in ["AZ900", "MS102"]:
        cert_total = sum(len(s["questions"]) for s in master["practice_sets"][cert_key])
        print(f"  {cert_key}: {len(master['practice_sets'][cert_key])} exams, {cert_total} questions")
        total += cert_total
    print(f"  GRAND TOTAL: {total} questions")

    return master


def validate_all_questions(master):
    """Validate all questions have required fields and correct structure."""
    errors = 0
    for cert_key in ["AZ900", "MS102"]:
        for exam_set in master["practice_sets"][cert_key]:
            for q in exam_set["questions"]:
                qid = q.get("id", "UNKNOWN")
                required = ["id", "domain", "type", "stem", "choices", "answer", "explanations", "tip"]
                for field in required:
                    if field not in q:
                        print(f"  ERROR: {qid} missing field '{field}'")
                        errors += 1
                if len(q.get("choices", [])) != 4:
                    print(f"  ERROR: {qid} has {len(q.get('choices', []))} choices (expected 4)")
                    errors += 1
                if len(q.get("explanations", [])) != 4:
                    print(f"  ERROR: {qid} has {len(q.get('explanations', []))} explanations (expected 4)")
                    errors += 1

    if errors == 0:
        print("\n  ALL QUESTIONS VALIDATED OK - no errors found")
    else:
        print(f"\n  FOUND {errors} ERRORS - fix before building HTML")

    return errors == 0


if __name__ == "__main__":
    print("=" * 60)
    print("EXAM COMBINER - Building master question bank")
    print("=" * 60)

    master = build_master_json()

    print("\n" + "=" * 60)
    print("VALIDATION")
    print("=" * 60)
    valid = validate_all_questions(master)

    if valid:
        print("\n" + "=" * 60)
        print("SUCCESS! All exams combined and validated.")
        print("=" * 60)
        print("\nNext step: Run build_html.py to generate the offline HTML simulator")
    else:
        print("\nFix errors before proceeding.")

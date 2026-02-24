#!/usr/bin/env python3
"""
Shuffle answer positions so the correct answer isn't always B.
Maintains the link between choices, explanations, and answer index.
Targets roughly 25% per option (A/B/C/D).
"""

import json
import os
import random

random.seed(42)  # Reproducible shuffles

QUESTIONS_DIR = "questions"

def shuffle_question(q):
    """Shuffle choices and explanations together, update answer index."""
    old_answer_idx = q["answer"][0]

    # Create paired list: (choice, explanation, was_correct)
    pairs = []
    for i in range(4):
        pairs.append({
            "choice": q["choices"][i],
            "explanation": q["explanations"][i],
            "is_correct": (i == old_answer_idx)
        })

    # Shuffle
    random.shuffle(pairs)

    # Rebuild
    q["choices"] = [p["choice"] for p in pairs]
    q["explanations"] = [p["explanation"] for p in pairs]
    q["answer"] = [i for i, p in enumerate(pairs) if p["is_correct"]]

    return q


def process_all():
    from collections import Counter

    all_answers_before = []
    all_answers_after = []

    for cert in ['az900', 'ms102']:
        for exam_num in range(1, 6):
            complete_file = os.path.join(QUESTIONS_DIR, f"{cert}_exam{exam_num}_complete.json")
            if not os.path.exists(complete_file):
                print(f"SKIP: {complete_file} not found")
                continue

            with open(complete_file) as f:
                questions = json.load(f)

            # Record before
            for q in questions:
                all_answers_before.append(q["answer"][0])

            # Shuffle each question
            for q in questions:
                shuffle_question(q)

            # Record after
            for q in questions:
                all_answers_after.append(q["answer"][0])

            # Write back
            with open(complete_file, 'w') as f:
                json.dump(questions, f, indent=2)

            # Also rebuild batch files from complete
            # (we don't need to - the complete file is the source of truth)

            dist = Counter(q["answer"][0] for q in questions)
            labels = {0:'A', 1:'B', 2:'C', 3:'D'}
            d = ', '.join(f"{labels[k]}:{dist.get(k,0)}" for k in range(4))
            print(f"  {cert.upper()} Exam {exam_num}: {d}")

    # Overall stats
    labels = {0:'A', 1:'B', 2:'C', 3:'D'}
    print(f"\nBEFORE shuffle:")
    cb = Counter(all_answers_before)
    for k in range(4):
        print(f"  {labels[k]}: {cb.get(k,0)} ({cb.get(k,0)/len(all_answers_before)*100:.1f}%)")

    print(f"\nAFTER shuffle:")
    ca = Counter(all_answers_after)
    for k in range(4):
        print(f"  {labels[k]}: {ca.get(k,0)} ({ca.get(k,0)/len(all_answers_after)*100:.1f}%)")


if __name__ == "__main__":
    print("Shuffling answer positions...\n")
    process_all()
    print("\nDone! All complete JSON files updated.")

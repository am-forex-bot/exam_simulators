#!/usr/bin/env python3
"""Build the AZ-900 Real Exam Simulator HTML from the MS-102 template and AZ-900 JSON data."""

import json

# 1. Read all 5 AZ-900 JSON files
exam_files = [
    ("/home/user/exam_simulators/questions/az900_exam1_complete.json", "Practice Exam 1"),
    ("/home/user/exam_simulators/questions/az900_exam2_complete.json", "Practice Exam 2"),
    ("/home/user/exam_simulators/questions/az900_exam3_complete.json", "Practice Exam 3"),
    ("/home/user/exam_simulators/questions/az900_exam4_complete.json", "Practice Exam 4"),
    ("/home/user/exam_simulators/questions/az900_exam5_complete.json", "Practice Exam 5"),
]

exams = []
for filepath, title in exam_files:
    with open(filepath, 'r') as f:
        questions = json.load(f)
    exams.append({"title": title, "questions": questions})
    print(f"  Loaded {filepath}: {len(questions)} questions")

# 2. Read the MS-102 template
with open('/home/user/exam_simulators/ms102_real_exam_simulator.html', 'r') as f:
    lines = f.readlines()

print(f"\nMS-102 template: {len(lines)} lines")

# 3. Build the EXAMS data line
exams_json = json.dumps(exams, ensure_ascii=False)
exams_line = f"var EXAMS = {exams_json};\n"

# 4. Assemble the new HTML
# Lines 1-55 (index 0-54): HTML header + CSS + body opening (before <script>)
# Line 56 (index 55): <script>
# Line 57 (index 56): var EXAMS = ... (data line - replace)
# Line 58 (index 57): empty
# Line 59+ (index 58+): var STATE and all JS logic

output_lines = []

# Copy lines 1-56 (indices 0-55), making substitutions
for i in range(56):
    line = lines[i]
    # Title tag
    line = line.replace('MS-102 Real Exam Simulator', 'AZ-900 Real Exam Simulator')
    # Brand text
    # Pill text - keep same since both have 250 questions and 5 exams
    output_lines.append(line)

# Add the EXAMS data line (replacing line 57)
output_lines.append(exams_line)

# Copy lines 58+ (indices 57+), making substitutions
for i in range(57, len(lines)):
    line = lines[i]
    # Replace timer durations
    # Line 59: durationSec: 100*60
    line = line.replace('durationSec: 100*60', 'durationSec: 45*60')
    # Line 102: 100 mins
    line = line.replace('100 mins', '45 mins')
    # Line 118: 100 * 60
    line = line.replace('100 * 60', '45 * 60')
    output_lines.append(line)

# 5. Write the output file
output_path = '/home/user/exam_simulators/az900_real_exam_simulator.html'
with open(output_path, 'w') as f:
    f.writelines(output_lines)

print(f"\nWrote {output_path}")
print(f"Output: {len(output_lines)} lines, {sum(len(l) for l in output_lines)} bytes")

# 6. Verification
print("\n--- Verification ---")

# Re-read and verify
with open(output_path, 'r') as f:
    content = f.read()

# Check title
assert 'AZ-900 Real Exam Simulator' in content, "FAIL: Title not found"
assert 'MS-102' not in content, "FAIL: MS-102 reference still present"
print("OK: Title is AZ-900 Real Exam Simulator, no MS-102 references")

# Check timer
assert '45*60' in content or '45 * 60' in content, "FAIL: 45-minute timer not found"
assert '100*60' not in content and '100 * 60' not in content, "FAIL: 100-minute timer still present"
assert '45 mins' in content, "FAIL: '45 mins' text not found"
assert '100 mins' not in content, "FAIL: '100 mins' text still present"
print("OK: Timer set to 45 minutes")

# Check pill
assert 'Offline &#x2022; 250 questions &#x2022; 5 practice exams' in content, "FAIL: Pill text not found"
print("OK: Pill text present")

# Check question counts via JSON extraction
import re
m = re.search(r'var EXAMS = (\[.*?\]);\s*\n', content, re.DOTALL)
if m:
    parsed_exams = json.loads(m.group(1))
    print(f"\nFound {len(parsed_exams)} exams:")
    total = 0
    for exam in parsed_exams:
        qcount = len(exam['questions'])
        total += qcount
        print(f"  {exam['title']}: {qcount} questions")
    print(f"  Total: {total} questions")
    assert len(parsed_exams) == 5, f"FAIL: Expected 5 exams, got {len(parsed_exams)}"
    assert total == 250, f"FAIL: Expected 250 questions, got {total}"
    for exam in parsed_exams:
        assert len(exam['questions']) == 50, f"FAIL: {exam['title']} has {len(exam['questions'])} questions"
    print("\nAll 5 exams with 50 questions each - PASS")
else:
    print("FAIL: Could not parse EXAMS data")

# Check self-contained (no external script/link refs)
assert '<link rel="stylesheet"' not in content, "FAIL: External CSS found"
assert '<script src=' not in content, "FAIL: External JS found"
print("OK: File is self-contained")

print("\n=== BUILD SUCCESSFUL ===")

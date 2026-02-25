#!/usr/bin/env python3
"""Build the dual exam simulator (AZ-900 + MS-102) with real-life-like questions.

Extracts questions from both single-exam simulators and embeds them into
the dual simulator HTML template.
"""

import json
import re
from datetime import datetime, timezone


def extract_exams(html_path):
    """Extract the EXAMS array from a single-exam simulator HTML file."""
    with open(html_path) as f:
        html = f.read()
    m = re.search(r'var EXAMS\s*=\s*(\[.+?\]);\s*\n', html, re.DOTALL)
    if not m:
        raise ValueError(f"Could not find var EXAMS in {html_path}")
    return json.loads(m.group(1))


def build_bank(az900_exams, ms102_exams):
    """Build the BANK object in the dual simulator format."""
    # Count domain distribution from first AZ-900 exam
    az_domains = {}
    for q in az900_exams[0]["questions"]:
        az_domains[q["domain"]] = az_domains.get(q["domain"], 0) + 1

    ms_domains = {}
    for q in ms102_exams[0]["questions"]:
        ms_domains[q["domain"]] = ms_domains.get(q["domain"], 0) + 1

    bank = {
        "meta": {
            "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "note": "Original practice questions aligned to public exam objectives. "
                    "Not official Microsoft exam questions; no copyrighted exam items included."
        },
        "exams": [
            {
                "code": "AZ900",
                "name": "AZ-900: Microsoft Azure Fundamentals",
                "pass_scaled": 700,
                "max_scaled": 1000,
                "domains": [{"name": d, "count": c} for d, c in az_domains.items()]
            },
            {
                "code": "MS102",
                "name": "MS-102: Microsoft 365 Endpoint Administrator",
                "pass_scaled": 700,
                "max_scaled": 1000,
                "domains": [{"name": d, "count": c} for d, c in ms_domains.items()]
            }
        ],
        "practice_sets": {
            "AZ900": [],
            "MS102": []
        }
    }

    for i, exam in enumerate(az900_exams):
        bank["practice_sets"]["AZ900"].append({
            "set": i + 1,
            "title": exam["title"],
            "questions": exam["questions"]
        })

    for i, exam in enumerate(ms102_exams):
        bank["practice_sets"]["MS102"].append({
            "set": i + 1,
            "title": exam["title"],
            "questions": exam["questions"]
        })

    return bank


# Template: HTML + CSS (lines 1-61 of the dual simulator, adapted)
TEMPLATE_TOP = r"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dual Exam Simulator (AZ-900 + MS-102) v10 – Real Exam Style</title>
<style>
  :root { --bg:#0b0f14; --card:#121a24; --muted:#93a4b8; --text:#e7eef7; --accent:#7dd3fc; --good:#34d399; --bad:#fb7185; }
  body { margin:0; font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; background:var(--bg); color:var(--text); }
  .wrap { max-width: 980px; margin: 0 auto; padding: 18px; }
  .topbar { display:flex; gap:12px; align-items:center; justify-content:space-between; flex-wrap:wrap; }
  .brand { font-weight:800; letter-spacing:0.2px; }
  .pill { display:inline-flex; gap:8px; align-items:center; padding:8px 10px; border-radius:999px; background:rgba(255,255,255,0.06); color:var(--muted); font-size:12px; }
  .grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:12px; margin-top:14px; }
  .card { background:var(--card); border:1px solid rgba(255,255,255,0.08); border-radius:16px; padding:14px; box-shadow: 0 10px 20px rgba(0,0,0,0.25); }
  .muted { color:var(--muted); white-space:pre-wrap; }
  .tiny { font-size:12px; color:var(--muted); }
  .btnrow { display:flex; gap:10px; flex-wrap:wrap; margin-top:10px; }
  button { cursor:pointer; border:1px solid rgba(255,255,255,0.12); background:rgba(255,255,255,0.06); color:var(--text); padding:10px 12px; border-radius:12px; font-weight:700; }
  button.primary { background: rgba(125,211,252,0.18); border-color: rgba(125,211,252,0.35); }
  button.danger { background: rgba(251,113,133,0.15); border-color: rgba(251,113,133,0.35); }
  button:disabled { opacity:0.5; cursor:not-allowed; }
  .linkbtn { border:none; background:none; color:var(--accent); padding:0; font-weight:800; }
  .qnum { font-weight:900; }
  .domain { font-size:12px; color:var(--muted); margin-top:4px; }
  .stem { margin:10px 0 12px 0; line-height:1.35; white-space:pre-wrap; }
  .choices { display:flex; flex-direction:column; gap:10px; }
  .choice { display:flex; gap:10px; align-items:flex-start; padding:10px; border-radius:12px; background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); }
  .choice input { margin-top:2px; }
  .progress { height:10px; border-radius:999px; background:rgba(255,255,255,0.06); overflow:hidden; margin-top:12px; }
  .bar { height:10px; width:0%; background:rgba(125,211,252,0.8); }
  .reveal { margin-top:12px; padding:12px; border-radius:14px; border:1px solid rgba(255,255,255,0.10); background:rgba(255,255,255,0.04); }
  .reveal.good { border-color: rgba(52,211,153,0.35); background: rgba(52,211,153,0.10); }
  .reveal.bad { border-color: rgba(251,113,133,0.35); background: rgba(251,113,133,0.10); }
  .sectionTitle { margin-top:10px; font-weight:900; }
  .bullet { margin:6px 0 0 0; padding-left:18px; }
  .bullet li { margin:8px 0; color:var(--muted); }
  .bullet li b { color:var(--text); }
  .kpi { display:flex; gap:10px; flex-wrap:wrap; margin-top:10px; }
  .k { padding:8px 10px; border-radius:12px; background:rgba(255,255,255,0.06); font-size:12px; color:var(--muted); }
  .k b { color:var(--text); }
  .hr { height:1px; background:rgba(255,255,255,0.08); margin:14px 0; }
  .footer { margin-top:18px; color:var(--muted); font-size:12px; }
  .pass { color: var(--good); font-weight:900; }
  .fail { color: var(--bad); font-weight:900; }
</style>
</head>
<body>
<div class="wrap">
  <div class="topbar">
    <div class="brand">Dual Exam Simulator <span class="tiny">v10 &bull; Real exam-style scenarios</span></div>
    <div class="pill" id="metaPill">Offline &bull; Single-file &bull; ES5</div>
  </div>

  <div id="viewHome"></div>
  <div id="viewPicker" style="display:none;"></div>
  <div id="viewExam" style="display:none;"></div>
  <div class="footer" id="footerNote"></div>
</div>

<script>
"""

TEMPLATE_JS = r"""
function $(id) { return document.getElementById(id); }
function esc(s) {
  if (s === null || s === undefined) return '';
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;').replace(/'/g,'&#039;');
}
function clone(obj) { return JSON.parse(JSON.stringify(obj)); }
function arrHas(a, v) { for (var i=0;i<a.length;i++) if (a[i]===v) return true; return false; }
function setEq(a,b) {
  if (a.length !== b.length) return false;
  for (var i=0;i<a.length;i++) if (!arrHas(b,a[i])) return false;
  return true;
}
function fmtTime(sec) {
  sec = Math.max(0, Math.floor(sec));
  var m = Math.floor(sec/60), s = sec % 60;
  return (m<10?'0':'')+m+':' + (s<10?'0':'')+s;
}
function getExamMeta(code) {
  for (var i=0;i<BANK.exams.length;i++) if (BANK.exams[i].code===code) return BANK.exams[i];
  return null;
}
function defaultDuration(code) {
  if (code === 'AZ900') return 45*60;
  if (code === 'MS102') return 100*60;
  return 90*60;
}

var STATE = {
  examCode:null, examName:null, setIndex:null, questions:null,
  idx:0, answers:{}, revealed:{}, startedAt:null, timerId:null,
  durationSec:90*60, finished:false
};

function renderHome() {
  $('viewPicker').style.display='none';
  $('viewExam').style.display='none';
  var h='';
  h+='<div class="card">';
  h+='<h2 style="margin:0 0 8px 0;">Pick an exam</h2>';
  h+='<div class="muted">Real exam-style, scenario-based practice questions with Microsoft-style distractors and detailed explanations.</div>';
  h+='<div class="grid">';
  for (var i=0;i<BANK.exams.length;i++) {
    var ex=BANK.exams[i];
    h+='<div class="card">';
    h+='<h3 style="margin:0 0 6px 0;">'+esc(ex.name)+'</h3>';
    h+='<div class="tiny">5 practice exams &bull; 50 questions each &bull; domain-weighted &bull; shuffled answers</div>';
    h+='<div class="kpi">';
    h+='<div class="k"><b>Pass</b> '+ex.pass_scaled+'/'+ex.max_scaled+'</div>';
    h+='<div class="k"><b>Q</b> 50</div>';
    h+='<div class="k"><b>Time</b> '+(defaultDuration(ex.code)/60)+' mins</div>';
    h+='</div>';
    h+='<div class="btnrow"><button class="primary" onclick="pickExam(\''+ex.code+'\')">Choose</button></div>';
    h+='</div>';
  }
  h+='</div>';
  h+='<div class="hr"></div>';
  h+='<div class="tiny">Scoring: revealed questions only &rarr; raw% and approximate scaled score (0&ndash;1000). Pass at 700.</div>';
  h+='</div>';
  $('viewHome').innerHTML=h;
  $('footerNote').innerHTML=esc(BANK.meta.note)+' &bull; Generated: '+esc(BANK.meta.generated_utc);
}

function pickExam(code) {
  var meta=getExamMeta(code);
  STATE.examCode=code;
  STATE.examName=meta?meta.name:code;
  renderPicker();
}

function renderPicker() {
  $('viewHome').innerHTML='';
  $('viewExam').style.display='none';
  $('viewPicker').style.display='';
  var sets=BANK.practice_sets[STATE.examCode]||[];
  var h='';
  h+='<div class="card">';
  h+='<div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start;">';
  h+='<div><h2 style="margin:0 0 6px 0;">'+esc(STATE.examName)+'</h2><div class="muted">Choose a practice exam.</div></div>';
  h+='<button class="linkbtn" onclick="goHome()">&larr; Back</button>';
  h+='</div>';
  h+='<div class="grid">';
  for (var i=0;i<sets.length;i++) {
    var s=sets[i];
    h+='<div class="card">';
    h+='<h3 style="margin:0 0 6px 0;">'+esc(s.title)+'</h3>';
    h+='<div class="kpi">';
    h+='<div class="k"><b>Questions</b> 50</div>';
    h+='<div class="k"><b>Time</b> '+(defaultDuration(STATE.examCode)/60)+' mins</div>';
    h+='</div>';
    h+='<div class="btnrow"><button class="primary" onclick="startExam('+s.set+')">Start</button></div>';
    h+='</div>';
  }
  h+='</div></div>';
  $('viewPicker').innerHTML=h;
}

function goHome() {
  resetState();
  $('viewHome').innerHTML='';
  $('viewPicker').innerHTML='';
  $('viewExam').innerHTML='';
  $('viewHome').style.display='';
  renderHome();
}
function resetState() {
  if (STATE.timerId) clearInterval(STATE.timerId);
  STATE={examCode:null, examName:null, setIndex:null, questions:null, idx:0, answers:{}, revealed:{}, startedAt:null, timerId:null, durationSec:90*60, finished:false};
}

function startExam(setIndex) {
  STATE.setIndex=setIndex;
  STATE.durationSec=defaultDuration(STATE.examCode);
  STATE.startedAt=new Date().getTime();
  STATE.answers={}; STATE.revealed={}; STATE.idx=0; STATE.finished=false;

  var sets=BANK.practice_sets[STATE.examCode]||[];
  var picked=null;
  for (var i=0;i<sets.length;i++) if (sets[i].set===setIndex) picked=sets[i];
  STATE.questions=picked?clone(picked.questions):[];

  $('viewPicker').style.display='none';
  $('viewExam').style.display='';
  tickTimer();
  if (STATE.timerId) clearInterval(STATE.timerId);
  STATE.timerId=setInterval(tickTimer,1000);
  renderQuestion();
}

function remainingSec() {
  if (!STATE.startedAt) return STATE.durationSec;
  var elapsed=(new Date().getTime()-STATE.startedAt)/1000;
  return Math.max(0, STATE.durationSec - elapsed);
}
function tickTimer() {
  if (!STATE.startedAt || STATE.finished) return;
  var rem=remainingSec();
  $('metaPill').innerHTML='Offline &bull; '+esc(STATE.examCode)+' &bull; Time left: '+fmtTime(rem);
  if (rem<=0) finishExam(true);
}

function toggleChoice(qid, idx) {
  var q=null;
  for (var i=0;i<STATE.questions.length;i++) if (STATE.questions[i].id===qid) q=STATE.questions[i];
  if (!q) return;
  if (STATE.revealed[qid]===true) return;

  var sel=STATE.answers[qid]||[];
  if (q.type==='single') sel=[idx];
  else {
    if (arrHas(sel, idx)) {
      var n=[]; for (var j=0;j<sel.length;j++) if (sel[j]!==idx) n.push(sel[j]);
      sel=n;
    } else sel.push(idx);
  }
  STATE.answers[qid]=sel;
  renderQuestion();
}

function gradeQuestion(q) {
  var sel=(STATE.answers[q.id]||[]).slice().sort(function(a,b){return a-b;});
  var ans=(q.answer||[]).slice().sort(function(a,b){return a-b;});
  return setEq(sel, ans);
}

function gradeAll() {
  var correct=0, revealed=0, answered=0;
  var perDomain={};
  for (var i=0;i<STATE.questions.length;i++) {
    var q=STATE.questions[i];
    var sel=STATE.answers[q.id]||[];
    if (sel.length>0) answered++;
    if (STATE.revealed[q.id]===true) {
      revealed++;
      if (!perDomain[q.domain]) perDomain[q.domain]={total:0, correct:0};
      perDomain[q.domain].total++;
      if (gradeQuestion(q)) { correct++; perDomain[q.domain].correct++; }
    }
  }
  var denom=Math.max(1, revealed);
  var raw=Math.round((correct/denom)*100);
  var scaled=Math.round((correct/denom)*1000);
  return {correct:correct,revealed:revealed,answered:answered,rawPct:raw,scaled:scaled,perDomain:perDomain};
}

function revealAnswer() {
  var q=STATE.questions[STATE.idx];
  if (!q) return;
  STATE.revealed[q.id]=true;
  renderQuestion();
}

function prevQ() { if (STATE.idx>0) { STATE.idx--; renderQuestion(); } }
function nextQ() { if (STATE.idx<STATE.questions.length-1) { STATE.idx++; renderQuestion(); } }

function confirmExit() {
  var ok=confirm('Exit exam? Your progress in this attempt will be lost.');
  if (ok) renderPicker();
}

function renderQuestion() {
  var q=STATE.questions[STATE.idx];
  if (!q) return;
  var total=STATE.questions.length;
  var selected=STATE.answers[q.id]||[];
  var revealed=STATE.revealed[q.id]===true;

  var h='';
  h+='<div class="card">';
  h+='<div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start;">';
  h+='<div><div class="qnum">Question '+(STATE.idx+1)+' of '+total+'</div>';
  h+='<div class="domain">'+esc(q.domain)+' &bull; '+(q.type==='multi' ? ('Select '+q.pick) : 'Select 1')+'</div></div>';
  h+='<button class="linkbtn" onclick="confirmExit()">Exit</button>';
  h+='</div>';

  h+='<div class="progress"><div class="bar" style="width:'+Math.round((STATE.idx)/Math.max(1,total-1)*100)+'%"></div></div>';
  h+='<div class="stem">'+esc(q.stem)+'</div>';

  h+='<div class="choices">';
  for (var i=0;i<q.choices.length;i++) {
    var isSel=arrHas(selected,i);
    var inputType=(q.type==='multi')?'checkbox':'radio';
    var disabled=revealed?'disabled':'';
    var checked=isSel?'checked':'';
    var name='q_'+q.id;
    h+='<label class="choice">';
    h+='<input '+disabled+' '+checked+' type="'+inputType+'" name="'+esc(name)+'" onclick="toggleChoice(\''+q.id+'\','+i+')" />';
    h+='<div><b>'+String.fromCharCode(65+i)+'.</b> '+esc(q.choices[i])+'</div>';
    h+='</label>';
  }
  h+='</div>';

  h+='<div class="btnrow">';
  h+='<button onclick="prevQ()" '+(STATE.idx===0?'disabled':'')+'>&#8592; Previous</button>';
  h+='<button onclick="nextQ()" '+(STATE.idx===total-1?'disabled':'')+'>Next &#8594;</button>';
  h+='<button class="primary" onclick="revealAnswer()">Reveal answer</button>';
  h+='<button class="danger" onclick="finishExam(false)">Finish exam</button>';
  h+='</div>';

  if (revealed) {
    var isCorrect=gradeQuestion(q);
    var sel=(STATE.answers[q.id]||[]);
    var selTxt = sel.length ? sel.map(function(x){return String.fromCharCode(65+x);}).join(', ') : '\u2014';
    var ansTxt = (q.answer||[]).map(function(x){return String.fromCharCode(65+x);}).join(', ');
    h+='<div class="reveal '+(isCorrect?'good':'bad')+'">';
    h+='<div style="font-weight:900;">'+(isCorrect?'\u2705 Correct.':'\u274c Incorrect.')+'</div>';
    h+='<div class="tiny">You chose: <b>'+esc(selTxt)+'</b> &bull; Correct answer: <b>'+esc(ansTxt)+'</b></div>';

    h+='<div class="sectionTitle">Why '+esc(ansTxt)+' is right</div>';
    h+='<ul class="bullet">';
    for (var j=0;j<q.answer.length;j++) {
      var idx=q.answer[j];
      h+='<li><b>'+String.fromCharCode(65+idx)+'. '+esc(q.choices[idx])+'</b> &mdash; '+esc(q.explanations[idx]||'')+'</li>';
    }
    h+='</ul>';

    h+='<div class="sectionTitle">Why the others fall short</div>';
    h+='<ul class="bullet">';
    for (var k=0;k<q.choices.length;k++) {
      if (arrHas(q.answer,k)) continue;
      h+='<li><b>'+String.fromCharCode(65+k)+'. '+esc(q.choices[k])+'</b> &mdash; '+esc(q.explanations[k]||'')+'</li>';
    }
    h+='</ul>';

    if (q.tip) h+='<div class="sectionTitle">Key concept to lock in</div><div class="muted">'+esc(q.tip)+'</div>';
    h+='</div>';
  }

  h+='</div>';

  var g=gradeAll();
  h+='<div class="card">';
  h+='<div class="kpi">';
  h+='<div class="k"><b>Answered</b> '+g.answered+'/'+total+'</div>';
  h+='<div class="k"><b>Revealed</b> '+g.revealed+'/'+total+'</div>';
  h+='<div class="k"><b>Raw</b> '+g.rawPct+'%</div>';
  h+='<div class="k"><b>Scaled</b> '+g.scaled+'/1000</div>';
  h+='</div>';
  h+='<div class="tiny">Raw/Scaled are computed from revealed questions only (so you can do full &ldquo;exam mode&rdquo; without revealing).</div>';
  h+='</div>';

  $('viewExam').innerHTML=h;
}

function finishExam(auto) {
  if (STATE.finished) return;
  STATE.finished=true;
  if (STATE.timerId) clearInterval(STATE.timerId);
  if (auto) for (var i=0;i<STATE.questions.length;i++) STATE.revealed[STATE.questions[i].id]=true;

  var meta=getExamMeta(STATE.examCode);
  var g=gradeAll();
  var pass=g.scaled >= (meta?meta.pass_scaled:700);

  var h='';
  h+='<div class="card">';
  h+='<div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start;">';
  h+='<div><h2 style="margin:0 0 6px 0;">Results: '+esc(STATE.examName)+' &mdash; Practice Exam '+STATE.setIndex+'</h2>';
  h+='<div class="muted">'+(auto?'Time expired &mdash; auto-finished.':'Finished.')+'</div></div>';
  h+='<button class="linkbtn" onclick="renderPicker()">&larr; Back to exams</button>';
  h+='</div>';

  h+='<div class="kpi">';
  h+='<div class="k"><b>Revealed</b> '+g.revealed+'/'+STATE.questions.length+'</div>';
  h+='<div class="k"><b>Correct</b> '+g.correct+'/'+g.revealed+'</div>';
  h+='<div class="k"><b>Raw</b> '+g.rawPct+'%</div>';
  h+='<div class="k"><b>Scaled</b> '+g.scaled+'/1000</div>';
  h+='<div class="k"><b>Verdict</b> <span class="'+(pass?'pass':'fail')+'">'+(pass?'PASS':'FAIL')+'</span></div>';
  h+='</div>';

  h+='<div class="hr"></div>';
  h+='<h3 style="margin:0 0 8px 0;">Domain breakdown (revealed questions)</h3>';
  h+='<div class="grid">';
  for (var d in g.perDomain) {
    if (!g.perDomain.hasOwnProperty(d)) continue;
    var st=g.perDomain[d];
    var pct=st.total?Math.round((st.correct/st.total)*100):0;
    h+='<div class="card"><h3 style="margin:0 0 6px 0;">'+esc(d)+'</h3>';
    h+='<div class="kpi"><div class="k"><b>Correct</b> '+st.correct+'/'+st.total+'</div><div class="k"><b>%</b> '+pct+'%</div></div></div>';
  }
  h+='</div>';

  h+='<div class="hr"></div>';
  h+='<div class="btnrow">';
  h+='<button class="primary" onclick="reviewIncorrect()">Review incorrect</button>';
  h+='<button onclick="restartSame()">Restart this exam</button>';
  h+='<button onclick="goHome()">Home</button>';
  h+='</div>';

  h+='<div class="tiny">Scaled score is an approximation designed to mimic the 700/1000 pass threshold.</div>';
  h+='</div>';

  $('viewExam').innerHTML=h;
  $('metaPill').innerHTML='Offline &bull; '+esc(STATE.examCode)+' &bull; Finished';
}

function reviewIncorrect() {
  for (var i=0;i<STATE.questions.length;i++) {
    var q=STATE.questions[i];
    if (STATE.revealed[q.id]===true && !gradeQuestion(q)) {
      STATE.finished=false;
      STATE.idx=i;
      renderQuestion();
      return;
    }
  }
  alert('No incorrect revealed questions found.');
}
function restartSame() { startExam(STATE.setIndex); }

renderHome();
"""

TEMPLATE_BOTTOM = """</script>
</body>
</html>"""


def main():
    az900_exams = extract_exams("/home/user/exam_simulators/az900_real_exam_simulator.html")
    ms102_exams = extract_exams("/home/user/exam_simulators/ms102_real_exam_simulator.html")

    bank = build_bank(az900_exams, ms102_exams)

    # Validate
    for code in ("AZ900", "MS102"):
        sets = bank["practice_sets"][code]
        assert len(sets) == 5, f"{code} should have 5 practice sets, got {len(sets)}"
        for s in sets:
            assert len(s["questions"]) == 50, f"{code} set {s['set']} should have 50 questions, got {len(s['questions'])}"
            for q in s["questions"]:
                assert len(q["choices"]) == 4, f"{q['id']} should have 4 choices"
                assert len(q["explanations"]) == 4, f"{q['id']} should have 4 explanations"
                assert len(q["answer"]) >= 1, f"{q['id']} should have at least 1 answer"

    total_az = sum(len(s["questions"]) for s in bank["practice_sets"]["AZ900"])
    total_ms = sum(len(s["questions"]) for s in bank["practice_sets"]["MS102"])
    print(f"AZ-900: {total_az} questions across {len(bank['practice_sets']['AZ900'])} exams")
    print(f"MS-102: {total_ms} questions across {len(bank['practice_sets']['MS102'])} exams")
    print(f"Total: {total_az + total_ms} questions")

    bank_json = json.dumps(bank, ensure_ascii=False, separators=(',', ':'))

    output = TEMPLATE_TOP + "var BANK = " + bank_json + ";\n" + TEMPLATE_JS + TEMPLATE_BOTTOM

    outpath = "/home/user/exam_simulators/dual_exam_simulator_az900_ms102_v10_real_exam_style.html"
    with open(outpath, "w") as f:
        f.write(output)

    import os
    size = os.path.getsize(outpath)
    print(f"Written: {outpath}")
    print(f"Size: {size:,} bytes")


if __name__ == "__main__":
    main()

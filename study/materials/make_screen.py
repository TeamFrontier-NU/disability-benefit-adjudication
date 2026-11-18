"""Write records/00_screen.rec.md (the DDS fast-track screen and evidence list that opens each
case file) from the "screen" block of case.json.

    "screen": {
      "printed": "11/16/2026",
      "allegations": ["...", "..."],                 # SSA-3368 3.A in the claimant's words
      "cal": "MATCH - allegation 1 '...'",           # or "No match"
      "qdd": "Selected (score above threshold)",     # or "Not selected"
      "exhibits": [["1F", "Source", "dates", "pages", "received", "how received"], ...],
      "pending":  [["Source", "requested", "follow-up", "status"], ...]
    }

The sheet only shows what the existing process already produced (allegations, the QDD/CAL
flags, what arrived and how). It never states a medical finding.

Usage: python study/materials/make_screen.py C1 [C2 ...] | --all
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CASES = Path(__file__).resolve().parent / "cases"


T = {  # fixed text of the sheet, per language ({...} are filled in)
    "en": dict(dept="Case development worksheet - initial claim (Title II)", address="SSA / State DDS electronic folder",
               printed="Printed {d}", title="FAST-TRACK SCREEN AND EVIDENCE LIST",
               keys=["Claimant", "SSN", "Claim", "Filed", "Rec'd at DDS", "Alleged onset", "Field office", "Level",
                     "Case status"],
               claim="DIB initial", fo=" FO", level="Initial", status="Pending MER review",
               h1="1. AUTOMATED SCREEN (already completed at transfer from the field office)",
               p1="The application forms (SSA-16, SSA-3368-BK, SSA-827) were taken by the field office and screened by "
                  "the existing selection software on the alleged conditions in SSA-3368 Section 3.A. The forms are in "
                  "this file for reference only; they have not been checked against the medical evidence.",
               al_head="| # | Alleged condition (claimant's words, SSA-3368 3.A) |",
               sc_head="| Screen | Result |", cal="Compassionate Allowance (CAL) selection",
               qdd="Quick Disability Determination (QDD) model",
               flag="A CAL or QDD flag is based on the claimant's allegation only. It is not a finding.",
               h2="2. MEDICAL EVIDENCE OF RECORD IN FILE (Section F)",
               ex_head="| Exhibit | Source | Dates of service | Pages | Received | How received |",
               h3="3. REQUESTS NOT ANSWERED", pe_head="| Source | Requested | Follow-up | Status |",
               none="None outstanding", h4="4. EXAMINER ACTION",
               p4="Review the medical evidence of record and decide whether the claim stays on the fast track under "
                  "the study rules (condition, source of the key finding, duration)."),
    "es": dict(dept="Hoja de trabajo de desarrollo del caso - solicitud inicial (Título II)",
               address="Expediente electrónico SSA / DDS estatal", printed="Impreso {d}",
               title="EVALUACIÓN DE VÍA RÁPIDA Y LISTA DE PRUEBAS",
               keys=["Solicitante", "SSN", "Solicitud", "Presentada", "Recibida en DDS", "Inicio alegado",
                     "Oficina local", "Nivel", "Estado"],
               claim="DIB inicial", fo=" (oficina local)", level="Inicial", status="Pendiente de revisión médica",
               h1="1. EVALUACIÓN AUTOMÁTICA (ya realizada al transferir el caso desde la oficina local)",
               p1="La oficina local recibió los formularios de solicitud (SSA-16, SSA-3368-BK, SSA-827) y el programa de "
                  "selección existente los evaluó según las afecciones alegadas en la sección 3.A del SSA-3368. Los "
                  "formularios están en el expediente solo como referencia (en su versión oficial en inglés); no se "
                  "han cotejado con las pruebas médicas.",
               al_head="| # | Afección alegada (palabras del solicitante, SSA-3368 3.A) |",
               sc_head="| Evaluación | Resultado |", cal="Selección de Aprobación Compasiva (CAL)",
               qdd="Modelo de Determinación Rápida de Discapacidad (QDD)",
               flag="Una marca CAL o QDD se basa solo en lo que alega el solicitante. No es una conclusión médica.",
               h2="2. PRUEBAS MÉDICAS EN EL EXPEDIENTE (Sección F)",
               ex_head="| Anexo | Fuente | Fechas de atención | Páginas | Recibido | Forma de recepción |",
               h3="3. SOLICITUDES SIN RESPUESTA", pe_head="| Fuente | Solicitado | Seguimiento | Estado |",
               none="Ninguna pendiente", h4="4. ACCIÓN DEL EXAMINADOR",
               p4="Revise las pruebas médicas del expediente y decida si la solicitud sigue en la vía rápida según las "
                  "reglas del estudio (afección, fuente del hallazgo clave, duración)."),
    "zh": dict(dept="案件审查工作单——首次申请（第二编）", address="SSA / 州 DDS 电子案卷", printed="打印于 {d}",
               title="快速通道筛查与证据清单",
               keys=["申请人", "社会安全号", "申请类型", "提交日期", "DDS 收到日期", "申报发病日期", "受理办公室",
                     "审理级别", "案件状态"],
               claim="DIB 首次申请", fo=" 办公室", level="首次", status="待审查医疗证据",
               h1="1. 自动筛查（案件从受理办公室转来时已完成）",
               p1="申请表（SSA-16、SSA-3368-BK、SSA-827）由受理办公室接收，并已由现有的筛选软件根据 SSA-3368 第 3.A "
                  "部分填报的病情进行筛查。申请表仅作参考放在案卷中（为官方英文版）；尚未与医疗证据核对。",
               al_head="| # | 申报的病情（申请人原话，SSA-3368 3.A） |",
               sc_head="| 筛查 | 结果 |", cal="恻隐快速批准（CAL）筛选", qdd="快速残障认定（QDD）模型",
               flag="CAL 或 QDD 标记仅依据申请人的申报内容，不是医学结论。",
               h2="2. 案卷中的医疗证据（F 部分）",
               ex_head="| 证据编号 | 来源 | 就诊日期 | 页数 | 收到日期 | 收到方式 |",
               h3="3. 未获回复的调取请求", pe_head="| 来源 | 请求日期 | 催办日期 | 状态 |",
               none="无未结请求", h4="4. 审查员操作",
               p4="请审查案卷中的医疗证据，并根据本研究规则（病情、关键证据的来源、持续时间）决定该申请是否继续留在快速通道。"),
}


def make(cid: str, lang: str = "en") -> Path:
    """English from case.json "screen"; other languages from "screen_i18n"[lang] (same keys)."""
    case = json.loads((CASES / cid / "case.json").read_text(encoding="utf-8"))
    cl, cm, t = case["claimant"], case["claim"], T[lang]
    s = case["screen"] if lang == "en" else {**case["screen"], **case["screen_i18n"][lang]}
    last, first = cl["name"].replace(".", "").rsplit(" ", 1)[1], cl["name"].replace(".", "").rsplit(" ", 1)[0]
    al = "\n".join(f"| {i} | {a} |" for i, a in enumerate(s["allegations"], 1))
    ex = "\n".join("| " + " | ".join(e) + " |" for e in s["exhibits"])
    pend = "\n".join("| " + " | ".join(p) + " |" for p in s.get("pending", [])) or f"| {t['none']} | | | |"
    fo = cm["field_office"].replace(" Field Office", "") + t["fo"]
    vals = [f"{last.upper()}, {first.upper()}", cl["ssn"], t["claim"], cm["filed"], cm["dds_received"],
            cm["alleged_onset"], fo, t["level"], t["status"]]
    pat = "\n".join(f"  {k}: {v}" for k, v in zip(t["keys"], vals))
    text = f"""---
style: ehr
lang: {lang}
facility: Illinois Disability Determination Services
dept: {t['dept']}
address: {t['address']}
phone: "{t['printed'].format(d=s.get('printed', '11/16/2026'))}"
title: {t['title']}
patient:
{pat}
---
## {t['h1']}
{t['p1']}

{t['al_head']}
|---|---|
{al}

{t['sc_head']}
|---|---|
| {t['cal']} | {s['cal']} |
| {t['qdd']} | {s['qdd']} |

{t['flag']}

## {t['h2']}
{t['ex_head']}
|---|---|---|---|---|---|
{ex}

## {t['h3']}
{t['pe_head']}
|---|---|---|---|
{pend}

## {t['h4']}
{t['p4']}
"""
    sub = "records" if lang == "en" else f"records.{lang}"
    out = CASES / cid / sub / "00_screen.rec.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return out


if __name__ == "__main__":
    ids = sorted(p.name for p in CASES.iterdir() if (p / "case.json").exists()) if sys.argv[1:] == ["--all"] else sys.argv[1:]
    for c in ids:
        case = json.loads((CASES / c / "case.json").read_text(encoding="utf-8"))
        for lang in ["en"] + sorted(case.get("screen_i18n", {})):
            print("wrote", make(c, lang))

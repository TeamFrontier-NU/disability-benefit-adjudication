"""Verify, Score and Route steps.

Verify: check every quote against the cited page, and tag it with who wrote it.
Score:  apply the rule table to verified items only (the source rule).
Route:  fast track or human queue. There is no code path that returns a denial.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from datetime import date

from .models import Case, Item, ReadResult, RuleResult, Routing, RULE_SOURCES

VOCATIONAL = {"age_at_filing", "alleged_onset_date", "currently_working", "earnings_above_sga",
              "education_level", "past_work_skill"}
NEVER_COUNTS = {"alleged_condition", "listing_assertion"}  # routing hints only


def _norm(s: str) -> str:
    s = s.lower().replace("’", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"\s+", " ", s)
    return s.strip(" .;:,\"'")


def provenance_ok(case: Case, doc) -> bool:
    listed = {p.lower() for p in case.listed_providers}
    return doc.received_via == "dds_request" and doc.provider.lower() in listed


def verify(case: Case, read: ReadResult, safeguards: bool = True) -> list[Item]:
    """safeguards=False switches off the source rule and provenance check (demo only, to show why they matter)."""
    for it in read.items:
        doc = case.doc_for_page(it.page)
        if doc is None:
            it.verified, it.drop_reason = False, "cited page does not exist"
            continue
        it.doc_id, it.source_type = doc.doc_id, doc.source_type
        if not it.quote.strip() or _norm(it.quote) not in _norm(case.page_text(it.page)):
            it.verified, it.drop_reason = False, "quote not found on the cited page"
            continue
        it.verified = True
        if not safeguards:
            it.counts_for_rules = True
        elif it.field in NEVER_COUNTS:
            it.drop_reason = "claimant statement or label: routing hint only"
        elif it.field in VOCATIONAL:
            it.counts_for_rules = doc.source_type in {"application", "claimant_form"} | RULE_SOURCES
        elif doc.source_type not in RULE_SOURCES:
            it.drop_reason = "not from an acceptable medical source (source rule)"
        elif not provenance_ok(case, doc):
            it.drop_reason = "record not received from a listed provider (provenance check)"
        else:
            it.counts_for_rules = True
    for ev in read.evidence_for_approval:
        doc = case.doc_for_page(ev.get("page", -1))
        ev["verified"] = bool(doc) and _norm(ev["quote"]) in _norm(case.page_text(ev["page"]))
        ev["source_type"] = doc.source_type if doc else ""
    return read.items


# ----------------------------------------------------------------------------- scoring helpers

@dataclass
class Evidence:
    items: list[Item]
    k: int

    def get(self, fld, values=None) -> list[Item]:
        out = [i for i in self.items if i.counts_for_rules and i.field == fld]
        if values is not None:
            out = [i for i in out if i.value.strip().lower() in values]
        return out

    def supported(self, fld, values=None) -> tuple[bool, list[int]]:
        hits = self.get(fld, values)
        docs = {i.doc_id for i in hits}
        return len(docs) >= self.k, sorted({i.page for i in hits})

    def first_value(self, fld):
        hits = self.get(fld)
        return hits[0].value if hits else None


def _date(s):
    try:
        return date.fromisoformat(s)
    except (TypeError, ValueError):
        return None


def _criterion(name, ok, pages):
    return {"name": name, "met": bool(ok), "pages": pages}


def score(case: Case, items: list[Item], k: int = 1) -> list[RuleResult]:
    ev = Evidence(items, k)
    results = []

    # 11.08 spinal cord disorders
    a_ok, a_p = ev.supported("sci_complete_loss_of_function", {"yes"})
    b1, b1p = ev.supported("sci_disorganized_motor_two_extremities", {"yes"})
    b2, b2p = ev.supported("extreme_limitation_standing_balance_or_arms", {"yes"})
    inj = [_date(i.value) for i in ev.get("injury_or_onset_date")]
    inj = min([x for x in inj if x], default=None)
    latest_doc = max((_date(d.doc_date) for d in case.documents if d.source_type in RULE_SOURCES and _date(d.doc_date)),
                     default=None)
    months = (latest_doc - inj).days / 30.4 if inj and latest_doc else None
    dur_ok = months is not None and months >= 3
    met = (a_ok or (b1 and b2)) and dur_ok
    results.append(RuleResult("11.08", "Listing 11.08 spinal cord disorders", met, [
        _criterion("A: complete loss of function", a_ok, a_p),
        _criterion("B: disorganized motor function in two extremities", b1, b1p),
        _criterion("B: extreme limitation standing / balancing / arms", b2, b2p),
        _criterion(f"lasted 3 months after injury ({months:.0f} months)" if months else "lasted 3 months after injury (no injury date)",
                   dur_ok, [i.page for i in ev.get("injury_or_onset_date")])]))

    # 13.14 lung cancer
    sc, scp = ev.supported("lung_cancer_histology", {"small_cell"})
    nsc, nscp = ev.supported("lung_cancer_histology", {"non_small_cell"})
    adv, advp = ev.supported("lung_cancer_extent", {"metastatic", "inoperable", "unresectable", "recurrent"})
    results.append(RuleResult("13.14", "Listing 13.14 lung cancer", sc or (nsc and adv), [
        _criterion("B: small-cell carcinoma", sc, scp),
        _criterion("A: non-small-cell carcinoma", nsc, nscp),
        _criterion("A: inoperable, unresectable, recurrent or metastatic", adv, advp)]))

    # 6.03 chronic kidney disease with dialysis
    dia, diap = ev.supported("chronic_dialysis", {"yes"})
    results.append(RuleResult("6.03", "Listing 6.03 kidney disease on chronic dialysis", dia,
                              [_criterion("chronic hemodialysis or peritoneal dialysis", dia, diap)]))

    # Medical-vocational grid (sedentary, or light at 55+), unskilled or no past work
    age_v = ev.first_value("age_at_filing")
    age = int(age_v) if age_v and age_v.isdigit() else None
    sed, sedp = ev.supported("rfc_exertional_level", {"sedentary"})
    light, lightp = ev.supported("rfc_exertional_level", {"light"})
    edu = (ev.first_value("education_level") or "").lower()
    skill = (ev.first_value("past_work_skill") or "").lower()
    dur, durp = ev.supported("expected_duration_months", {"permanent"})
    if not dur:
        nums = [int(i.value) for i in ev.get("expected_duration_months") if i.value.isdigit()]
        dur, durp = (bool(nums) and max(nums) >= 12), [i.page for i in ev.get("expected_duration_months")]
    rfc_ok = (age is not None) and ((age >= 50 and sed) or (age >= 55 and light))
    edu_ok = edu in {"marginal", "limited", "high_school"}
    skill_ok = skill in {"none", "unskilled"}
    rule = ""
    if rfc_ok and edu_ok and skill_ok:
        older = age >= 55
        if sed:
            rule = {(False, True): "201.09", (False, False): "201.12", (True, True): "201.01", (True, False): "201.04"}[
                (older, edu in {"marginal", "limited"})]
        else:
            rule = "202.01" if edu in {"marginal", "limited"} else "202.04"
    results.append(RuleResult("grid", f"Medical-vocational grid{' rule ' + rule if rule else ''}",
                              bool(rule) and dur, [
        _criterion(f"age {age if age is not None else '?'}: 50+ with sedentary, or 55+ with light", rfc_ok,
                   sedp + lightp),
        _criterion(f"education: {edu or '?'} (no direct entry into skilled work)", edu_ok,
                   [i.page for i in ev.get("education_level")]),
        _criterion(f"past work: {skill or '?'} (unskilled or none)", skill_ok,
                   [i.page for i in ev.get("past_work_skill")]),
        _criterion("expected to last 12 months", dur, durp)]))

    # Mental disorders: never fast-tracked (design D5), shown for the human queue
    mh = ev.get("mental_disorder")
    results.append(RuleResult("12.x", "Mental disorders (12.03 / 12.04)", False,
                              [_criterion("mental disorder diagnosed by an acceptable medical source", bool(mh),
                                          [i.page for i in mh])],
                              note="Always sent to the human queue: the B criteria need an examiner's judgment."))
    return results


def flags_for(case: Case, items: list[Item], read: ReadResult) -> list[dict]:
    flags = []
    vocational = [i for i in items if i.verified and i.field in VOCATIONAL]
    if any(i.field == "currently_working" and i.value.lower() == "yes" for i in vocational):
        above = any(i.field == "earnings_above_sga" and i.value.lower() == "yes" for i in vocational)
        flags.append({"type": "step1", "detail": "Claimant reports current work" + (" above SGA" if above else ""),
                      "page": next(i.page for i in vocational if i.field == "currently_working")})
    for f in read.instruction_flags:
        flags.append({"type": "instruction", "detail": f"Text addressed to the AI: \"{f['quote'][:120]}\"",
                      "page": f.get("page")})
    for i in items:
        if i.verified and i.field == "visit_date":
            doc = case.doc_for_page(i.page)
            vd, dd = _date(i.value), _date(doc.doc_date) if doc else None
            if vd and dd and vd > dd:
                flags.append({"type": "consistency",
                              "detail": f"{doc.title} is dated {dd} but describes a visit on {vd}", "page": i.page})
    for d in case.documents:
        if d.source_type in RULE_SOURCES and not provenance_ok(case, d):
            flags.append({"type": "provenance",
                          "detail": f"{d.title}: {'handed in by the claimant' if d.received_via == 'claimant' else 'provider not listed in SSA-3368 section 8'}",
                          "page": min(d.pages) if d.pages else None})
    if case.prior_denial_months is not None and case.prior_denial_months <= 12:
        flags.append({"type": "repeat_filing", "detail": f"Prior denial {case.prior_denial_months} months ago", "page": None})
    dropped = [i for i in items if not i.verified]
    if dropped:
        flags.append({"type": "quote_check", "detail": f"{len(dropped)} item(s) dropped: quote not found", "page": None})
    for i in items:
        if i.verified and i.field == "listing_assertion":
            flags.append({"type": "label_only", "detail": f"Statement that the person meets Listing {i.value}, "
                                                          "which cannot count without findings", "page": i.page})
    return flags


BLOCKING = {"step1", "instruction", "consistency", "repeat_filing"}


def route(case: Case, items: list[Item], read: ReadResult, k: int = 1, safeguards: bool = True) -> Routing:
    results = score(case, items, k)
    flags = flags_for(case, items, read)
    if not safeguards:
        flags = [f for f in flags if f["type"] not in {"instruction", "consistency", "repeat_filing", "provenance"}]
    met = [r for r in results if r.met]
    reasons = []
    blocking = [f for f in flags if f["type"] in BLOCKING]
    # A provenance flag only blocks if a flagged document is what supports the met path.
    if not met:
        reasons.append("No covered rule path is fully met by verified medical-source evidence.")
    if blocking:
        reasons += [f"{f['type']}: {f['detail']}" for f in blocking]
    if any(i.verified is False and i.field not in {"alleged_condition"} for i in items) and met:
        # dropped quotes on fields used by the met path
        used = {p for r in met for c in r.criteria for p in c["pages"]}
        if any((not i.verified) and i.page in used for i in items):
            reasons.append("A quote supporting the rule could not be verified.")
    if met and not reasons:
        return Routing("fast_track", path=met[0].path, reasons=[f"Meets {met[0].label}"], flags=flags,
                       rule_results=results)
    mental = next(r for r in results if r.path == "12.x")
    if mental.criteria[0]["met"]:
        reasons.append("Mental disorder: examiner decides (design D5).")
    return Routing("human_queue", path=met[0].path if met else "", reasons=reasons, flags=flags,
                   rule_results=results)


@dataclass
class RunResult:
    case_id: str
    read: ReadResult
    routing: Routing
    seconds: float
    k: int
    extra: dict = field(default_factory=dict)


def run_case(case: Case, reader, k: int = 1, safeguards: bool = True) -> RunResult:
    t0 = time.time()
    try:
        read = reader.read(case)
    except Exception as e:  # any reader failure goes to a person, never to a decision
        read = ReadResult([], [], [], [f"Reader failed: {e}"], reader=getattr(reader, "name", "reader"))
    items = verify(case, read, safeguards)
    routing = route(case, items, read, k, safeguards)
    assert routing.route in {"fast_track", "human_queue"}  # the tool never denies
    return RunResult(case.case_id, read, routing, time.time() - t0, k, {"safeguards": safeguards})

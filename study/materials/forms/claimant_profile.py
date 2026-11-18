"""Turn a short claimant profile into the field values of the three official forms.

Writing 150+ field keys by hand per case is slow and error-prone. A profile holds the facts
once; `forms_from_profile()` maps them onto SSA-16, SSA-3368-BK and SSA-827 field keys (see
catalog/*.csv). Anything the profile cannot express can be added or overridden with
`extra["ssa-16"|"ssa-3368-bk"|"ssa-827"]`, which wins over the generated values.

    python study/materials/forms/claimant_profile.py cases/C1/profile.json   # prints the "forms" block

`build_case.py` calls this automatically when a case has `"profile"` instead of `"forms"`.
"""
from __future__ import annotations

import json
import sys

EDU = {"8": "P5_N5A_CB10", "9": "P5_N5A_CB11", "10": "P5_N5A_CB12", "11": "P5_N5A_CB13", "12": "P5_N5A_CB14",
       "GED": "P5_N5A_CB15", "college1": "P5_N5ACollege_CB1", "college2": "P5_N5ACollege_CB2",
       "college3": "P5_N5ACollege_CB3", "college4": "P5_N5ACollege_CB4"}


def _yn(v: bool) -> str:
    return "Yes" if v else "No"


def forms_from_profile(p: dict) -> dict:
    a = p["address"]  # {"street","city","state","zip","county"}
    s16 = {
        "Page1.N1FLD": p["name"], "Page1.N2FLD": p["ssn"], "Page1.N5AFLD": p["dob"],
        "Page1.N5BFLD": p["birthplace"], "Page1.N6ACB": "Yes",
        "Page1.N7BCB": _yn(bool(p.get("other_names"))), "Page1.N8ACB": "No",
        "Page1.N9FLD": p["onset"], "Page1.N12CB": "No", "Page1.N13ACB": "No", "Page1.N14ACB": "No",
        "Page2.N16FLD": "NONE", "Page3.N17ACB": "Yes", "Page3.N20ACB": "No",
        "Page3.N21AFLD2": p["earnings_last_year"], "Page3.N21BFLD2": p["earnings_this_year"],
        "Page3.N22ACB": "Yes", "Page3.QTwentytwo": _yn(p.get("work_related", False)), "Page3.Qtwentythree": "No",
        "Page4.N24ACB": "No", "Page4.N25ACB": _yn(bool(p.get("employer_pay"))), "Page4.N25BCB": "No",
        "Page4.N26CB": "No", "Page4.N27CB": "No", "Page4.N28CB": "No",
        "Page5.SignatureFLD": p.get("signature", p["name"]), "Page5.DateFLD": p["filed"],
        "Page5.TelephoneFLD": p["phone"], "Page5.RoutingFLD": "000000000",
        "Page5.AccountNumberFLD": "XXXXXX" + p["ssn"][-4:], "Page5.BankAccountCB": "checking",
        "Page5.ApplicantsAddressFLD": a["street"], "Page5.CityFLD": f"{a['city']}, {a['state']}",
        "Page5.ZIPFLD": a["zip"], "Page5.CountyFLD": a.get("county", ""),
        "Page7.SSAOfficeFLD": p["field_office"], "Page7.DateRecdFLD": p["filed"],
        "Page7.ClaimantFLD": p["name"], "Page7.SSClaimNumberFLD": p["ssn"] + " HA",
        "Page7.ContactFLD": p.get("fo_contact", "Claims Specialist"),
    }
    if p.get("other_names"):
        s16["Page1.N7CFLD"] = p["other_names"]
    if p.get("employer_pay"):
        s16["Page4.N25AFLD"] = p["employer_pay"]
    sp = p.get("spouse")
    if sp:
        s16.update({"Page2.N15ACB": "Yes", "Page2.N15BFLD2": sp["name"], "Page2.N15BFLD3": sp["married"],
                    "Page2.N15BFLD4": sp["where"], "Page2.N15BCB": "Clergymen", "Page2.N15BFLD5": sp["dob"],
                    "Page2.N15BFLD6": sp["ssn"], "Page2.N15CFLD1": "None", "Page2.N15DFLD1": "None"})
    else:
        s16["Page2.N15ACB"] = "No"
    emp = p["jobs"][0]
    s16.update({"Page3.N18TableR1C1": emp["employer"], "Page3.N18TableR1C2": emp["from"][:2],
                "Page3.N18TableR1C3": emp["from"][-4:], "Page3.N18TableR1C4": emp["to"][:2],
                "Page3.N18TableR1C5": emp["to"][-4:]})
    if p.get("ssa16_remarks"):
        s16["Page5.RemarksFLD"] = p["ssa16_remarks"]

    c = p["contact"]
    r = {
        "BodyPage3.P3_N1A_FLD": p["name"], "BodyPage3.P3_N1B_FLD": p["ssn"],
        "BodyPage3.P3_N1C_CB1" if p.get("other_names") else "BodyPage3.P3_N1C_CB2": True,
        "BodyPage3.P3_N1DAddress_FLD": a["street"], "BodyPage3.P3_N1DCity_FLD": a["city"],
        "BodyPage3.P3_N1DState_FLD": a["state"], "BodyPage3.P3_N1DZip_FLD": a["zip"],
        "BodyPage3.P3_N1EEmail_FLD": p.get("email", "none"), "BodyPage3.P3_N1FPhonePrim_FLD": p["phone"],
        "BodyPage3.P3_N1G_CB1": True, "BodyPage3.P3_N1H_CB1": True, "BodyPage3.P3_N1I_CB1": True,
        "BodyPage3.P3_IsThereSomeone_CB1": True, "BodyPage3.P3_N2A_FLD": c["name"],
        "BodyPage3.P3_N2B_FLD": c["relation"], "BodyPage3.P3_N2CAddress_FLD": c.get("address", "Same"),
        "BodyPage3.P3_N2D_FLD": c["phone"], "BodyPage4.P4_N2E_CB1": True,
        "BodyPage4.P4_N3BFeet_FLD": p["height"][0], "BodyPage4.P4_N3BInches_FLD": p["height"][1],
        "BodyPage4.P4_N3CPounds_FLD": p["weight"],
        "BodyPage4.P4_N4A_CB2": True, "BodyPage4.P4_N4CDate1_FLD": p["stopped_work"],
        "BodyPage4.P4_N4CWhyStop_CB1": True, "BodyPage5.P5_N4D_CB1": True, "BodyPage5.P5_N4E_CB2": True,
        "BodyPage5." + EDU[p["education"]["level"]]: True,
        "BodyPage5.P5_N5ADateComp_FLD": p["education"]["date"],
        "BodyPage5.P5_N5ASchoolName_FLD": p["education"]["school"],
        "BodyPage5.P5_N5B_CB1": True, "BodyPage6.P6_N5C_CB1": True, "BodyPage6.P6_N5D_FLD": "English",
        "BodyPage6.P6_N5E_CB1": True, "BodyPage6.P6_N5F_CB1": True, "BodyPage6.P6_N6A_CB2": True,
        "Bodypage7.P7_Checkthebox_CB2" if len(p["jobs"]) == 1 else "Bodypage7.P7_Checkthebox_CB1": True,
        "BodyPage9.P9_N6D_FLD": p["how_limits"],
        "BodyPage13.P13_N9_CB1": True,
        "BodyPage15.P15_Section12DateComp_FLD": p["filed"],
    }
    for i, cond in enumerate(p["conditions"][:5], 1):
        r[f"BodyPage4.P4_N3A{i}_FLD"] = cond
    for i, j in enumerate(p["jobs"][:5], 1):
        r.update({f"BodyPage6.P6_N6AJobTitle{i}_FLD": j["title"], f"BodyPage6.P6_N6ABusType{i}_FLD": j["business"],
                  f"BodyPage6.P6_N6AFrom{i}_FLD": j["from"], f"BodyPage6.P6_N6ATo{i}_FLD": j["to"],
                  f"BodyPage6.P6_N6AHourPerDay{i}_FLD": j["hours"], f"BodyPage6.P6_N6ADaysPerWk{i}_FLD": j["days"],
                  f"BodyPage6.P6_N6APayAmount{i}_FLD": j["pay"], f"BodyPage6.P6_N6APayFreq{i}_FLD": j["per"]})
    if len(p["jobs"]) == 1 and p.get("job_tasks"):
        r["Bodypage7.P7_N6B1_FLD"] = p["job_tasks"]
    if p.get("meds"):
        r["BodyPage9.P9_N7_CB2"] = True
        for i, (m, d, why) in enumerate(p["meds"][:11], 1):
            r.update({f"BodyPage9.P9_N7R{i}MedName_FLD": m, f"BodyPage9.P9_N7R{i}DocName_FLD": d,
                      f"BodyPage9.P9_N7R{i}Reason_FLD": why})
    else:
        r["BodyPage9.P9_N7_CB1"] = True
    r["BodyPage10.P10_N8A_CB2"] = True
    for i, pr in enumerate(p["providers"][:6], 1):
        pg = "BodyPage10.P10" if i <= 3 else "BodyPage11.P11"
        r.update({f"{pg}_N8A{i}FacilityName_FLD": pr["facility"], f"{pg}_N8A{i}ProviderName_FLD": pr.get("doctor", ""),
                  f"{pg}_N8A{i}MedCond_FLD": pr["for"], f"{pg}_N8A{i}Phone_FLD": pr.get("phone", ""),
                  f"{pg}_N8A{i}DateFirstSeen_FLD": pr["first"], f"{pg}_N8A{i}DateLastSeen_FLD": pr["last"],
                  f"{pg}_N8A{i}DateNextAppt_FLD": pr.get("next", ""), f"{pg}_N8A{i}Address_FLD": pr.get("street", ""),
                  f"{pg}_N8A{i}City_FLD": pr.get("city", ""), f"{pg}_N8A{i}State_FLD": pr.get("state", "")})
    tests = p.get("tests", {})
    if tests:
        r["BodyPage12.P12-N8B_CB2"] = True
        names = {"blood": "Blood", "mri": "MRI", "xray": "XRay", "biopsy": "Biopsy", "other": "Other", "ekg": "EKG"}
        for k, t in tests.items():
            n = names[k]
            if "part" in t:
                r[f"BodyPage12.P12-N8B{n}Test_FLD"] = t["part"]
            r[f"BodyPage12.P12-N8B{n}Name_FLD"] = t["where"]
            r[f"BodyPage12.P12-N8B{n}Date_FLD"] = t["date"]
    else:
        r["BodyPage12.P12-N8B_CB1"] = True
    if p.get("remarks"):
        r["Bodypage14.P14_Remarks_FLD"] = p["remarks"]
    if p.get("completed_by"):
        cb = p["completed_by"]
        r.update({"BodyPage15.P15_Section12WhoIsComp_CB4": True, "BodyPage15.P15_Section12Name_FLD": cb["name"],
                  "BodyPage15.P15_Section12Relation_FLD": cb["relation"],
                  "BodyPage15.P15_Section12DaytimePhone_FLD": cb.get("phone", "")})
    else:
        r["BodyPage15.P15_Section12WhoIsComp_CB1"] = True

    s827 = {"Page1.P1_Name1_FLD": p["name"], "Page1.P1_SSN1_FLD": p["ssn"], "Page1.P1_DOB_FLD": p["dob"],
            "Page1.P1_Signature1_FLD": p.get("signature", p["name"]), "Page1.P1_Date1_FLD": p["filed"],
            "Page1.P1_Address_FLD": a["street"], "Page1.P1_PhoneNum_FLD": p["phone"],
            "Page1.P1_City_FLD": a["city"], "Page1.P1_State_FLD": a["state"], "Page1.P1_Zip_FLD": a["zip"]}
    out = {"ssa-16": s16, "ssa-3368-bk": r, "ssa-827": s827}
    for form, vals in (p.get("extra") or {}).items():
        out[form].update(vals)
    return out


if __name__ == "__main__":
    print(json.dumps(forms_from_profile(json.load(open(sys.argv[1]))), indent=2))

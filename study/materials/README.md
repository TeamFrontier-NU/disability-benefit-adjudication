# Case materials: official SSA forms + realistic medical records

Builds each study case as the documents a DDS examiner actually receives: the claimant's filed
forms (the **official ssa.gov PDF templates**, filled in by script, never redrawn) and the
medical evidence as provider records (discharge summaries, clinic notes, imaging, pathology,
labs, letters), each stamped with how it reached the agency. No summaries.

```
study/materials/
  build_case.py            case.json + records -> study/content/cases/<ID>/*.pdf (one English set shown in every language)
  render_records.py        one .rec.md record -> PDF in the provider's own layout
  forms/
    templates/             blank SSA-16 (11-2022), SSA-3368-BK (06-2024), SSA-827 (06-2024), SSA-3373-BK (10-2026) from ssa.gov
    catalog/<form>.csv     every fillable field: key used in case.json, page, type, the form's own label
    fill_forms.py          fills the real fields, drops the XFA layer, flattens
    field_catalog.py       regenerates catalog/ after a new template revision
  cases/<ID>/
    case.json              claimant, claim dates, document order, form field values
    records/*.rec.md       medical records (YAML header + light markup, see render_records.py)
```

```bash
pip install pymupdf pypdf reportlab pyyaml
python study/materials/build_case.py C3        # or --all
python study/app/check_content.py              # checks AI quotes against the PDF text
```

## Writing a new case
1. Copy `cases/C3/` as a starting point. Keep **one** set of facts: dates, names, providers and
   tests on the SSA-3368 must line up with the records (with the usual claimant errors on purpose).
2. Look up field keys in `forms/catalog/*.csv` (search the label column). Text fields take a string;
   a yes/no pair takes the box's value (`"Page1.N6ACB": "Yes"`); single checkboxes take `true`.
3. Each record: a header (facility, title, patient grid, fax banner, exhibit, how it was received)
   and a body. Received line says whether the DDS requested it (`Health IT`, `Electronic Records
   Express`, `Fax`) or the claimant submitted it. Do not bold key findings: the reviewer has to find them.
4. Build, open the PDFs, then write the AI panel JSON (`content/ai/<ID>.en.json`) with `doc` + `page`.

Every record page carries a "SYNTHETIC RECORD" footer and all SSNs are in the invalid 000- range.

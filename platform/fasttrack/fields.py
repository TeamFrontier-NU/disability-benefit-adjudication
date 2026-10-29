"""The fixed checklist. The reader fills these fields; the rules read them.

Values are short normalized strings so the rules can compare them.
"""

FIELDS = {
    # Claimant and work (application, SSA-16, SSA-3368 sections 4-6)
    "age_at_filing": "Age in whole years on the filing date. Value: a number.",
    "alleged_onset_date": "Date the claimant says the condition stopped them working. Value: YYYY-MM-DD.",
    "currently_working": "Is the claimant working now? Value: yes or no.",
    "earnings_above_sga": "Any month since onset with earnings above the SGA amount ($1,550 on the form). Value: yes or no.",
    "education_level": "Highest schooling. Value: marginal (grade 6 or less), limited (grades 7-11), high_school (12 or GED), or college.",
    "past_work_skill": "Skill level of past work in the last 5 years. Value: none, unskilled, semiskilled, or skilled.",
    # Diagnoses and findings (medical records)
    "diagnosis": "A diagnosis made by a provider. Value: the diagnosis in a few words.",
    "alleged_condition": "A condition the claimant lists or describes themselves. Value: the condition in a few words.",
    "visit_date": "Date of a visit or exam described in the document. Value: YYYY-MM-DD.",
    "injury_or_onset_date": "Date of the injury or of the start of the medical condition. Value: YYYY-MM-DD.",
    "sci_complete_loss_of_function": "Spinal cord disorder: complete loss of function of both legs or both arms. Value: yes.",
    "sci_disorganized_motor_two_extremities": "Spinal cord disorder: disorganized motor function in two extremities. Value: yes.",
    "extreme_limitation_standing_balance_or_arms": "Extreme limitation in standing up from a seated position, balancing while standing or walking, or using the upper extremities. Value: yes.",
    "lung_cancer_histology": "Lung cancer cell type. Value: small_cell or non_small_cell.",
    "lung_cancer_extent": "Lung cancer extent. Value: metastatic, inoperable, unresectable, recurrent, or localized.",
    "chronic_dialysis": "Chronic hemodialysis or peritoneal dialysis for kidney disease. Value: yes.",
    "rfc_exertional_level": "A provider's statement of the most work the person can do. Value: sedentary, light, medium, or heavy.",
    "expected_duration_months": "How long the provider expects the limitation to last. Value: a number of months, or 'permanent'.",
    "mental_disorder": "A diagnosed mental disorder. Value: the diagnosis in a few words.",
    "listing_assertion": "A statement that the person 'meets' or 'equals' a Listing, with no findings given. Value: the Listing named.",
}

FIELD_NAMES = list(FIELDS)

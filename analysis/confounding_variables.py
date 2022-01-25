from cohortextractor import filter_codes_by_category, patients, combine_codelists
from codelists import *
from datetime import datetime, timedelta


def generate_confounding_variables(index_date):
    confounding_variables = dict(
    # DEMOGRAPHICS AND LIFESTYLE 
    ## self-reported ethnicity 
    ethnicity=patients.with_these_clinical_events(
        ethnicity_codes,
        returning="category",
        find_last_match_in_period=True,
        include_date_of_match=True,
        return_expectations={
            "category": {"ratios": {"1": 0.5, "2": 0.2, "3": 0.1, "4": 0.1, "5": 0.1}},
            "incidence": 0.75,
        },
    ), 
    # CLINICAL COMORBIDITIES 
    ## history of outcome events - for exclusion for each specific analysis 
    history_bells_palsy_gp=patients.with_these_clinical_events(
        bells_palsy_primary_care_codes,
        between=["index_date - 1 year", "index_date"],
        returning="binary_flag",
        return_expectations={"incidence": 0.15},
    ),
    history_bells_palsy_hospital=patients.admitted_to_hospital(
        with_these_diagnoses=bells_palsy_secondary_care_codes,
        between=["index_date - 1 year", "index_date"],
        returning="binary_flag",
        return_expectations={"incidence": 0.10},
    ),
    history_bells_palsy_emergency=patients.attended_emergency_care(
        with_these_diagnoses=bells_palsy_emergency_care_codes,
        between=["index_date - 1 year", "index_date"],
        returning="binary_flag",
        return_expectations={"incidence": 0.10},
    ), 
    history_any_bells_palsy=patients.satisfying("history_bells_palsy_gp OR history_bells_palsy_hospital OR history_bells_palsy_emergency"),

    history_transverse_myelitis_gp=patients.with_these_clinical_events(
        transverse_myelitis_primary_care_codes,
        between=["index_date - 1 year", "index_date"],
        returning="binary_flag",
        return_expectations={"incidence": 0.15},
    ),
    history_transverse_myelitis_hospital=patients.admitted_to_hospital(
        with_these_diagnoses=transverse_myelitis_secondary_care_codes,
        between=["index_date - 1 year", "index_date"],
        returning="binary_flag",
        return_expectations={"incidence": 0.10},
    ),
    history_any_transverse_myelitis=patients.satisfying("history_transverse_myelitis_gp OR history_transverse_myelitis_hospital"), 

    history_guillain_barre_gp=patients.with_these_clinical_events(
        guillain_barre_primary_care_codes,
        between=["index_date - 1 year", "index_date"],
        returning="binary_flag",
        return_expectations={"incidence": 0.15},
    ),
    history_guillain_barre_hospital=patients.admitted_to_hospital(
        with_these_diagnoses=guillain_barre_secondary_care_codes,
        between=["index_date - 1 year", "index_date"],
        returning="binary_flag",
        return_expectations={"incidence": 0.10},
    ),
    history_any_guillain_barre=patients.satisfying("history_guillain_barre_gp OR history_guillain_barre_hospital"), 

    ### MS/NO
    history_ms_no_gp=patients.with_these_clinical_events(
        ms_no_primary_care,
        on_or_before="index_date",
        returning="binary_flag",
        return_expectations={"incidence": 0.01},
    ),

    fu_ms_no_gp=patients.with_these_clinical_events(
        ms_no_primary_care,
        on_or_after="index_date",
        find_first_match_in_period=True, 
        returning="date", 
        date_format="YYYY-MM-DD",
        return_expectations={"date": {"earliest": "index_date"}, 
                             "incidence":0.01},
    ),

    ### CIDP
    history_cidp_gp=patients.with_these_clinical_events(
        cidp_primary_care,
        on_or_before="index_date",
        returning="binary_flag",
        return_expectations={"incidence": 0.01},
    ),

    fu_cidp_gp=patients.with_these_clinical_events(
        cidp_primary_care,
        on_or_after="index_date",
        find_first_match_in_period=True, 
        returning="date", 
        date_format="YYYY-MM-DD",
        return_expectations={"date": {"earliest": "index_date"}, 
                             "incidence":0.01},
    ),

    ## cancer 
    ### haematological 
    haem_cancer_date=patients.with_these_clinical_events(
        haematological_cancer,
        on_or_before="index_date",
        find_first_match_in_period=True, 
        returning="date",
        date_format="YYYY-MM", 
        return_expectations={"date": {"latest": "index_date"}},
    ),
    ### non-haematological 
    nonhaem_nonlung_cancer_date=patients.with_these_clinical_events(
        cancer_excluding_lung_and_haematological,
        on_or_before="index_date",
        find_first_match_in_period=True, 
        returning="date",
        date_format="YYYY-MM", 
        return_expectations={"date": {"latest": "index_date"}},
    ),
    ### lung
    lung_cancer_date=patients.with_these_clinical_events(
        lung_cancer,
        on_or_before="index_date",
        find_first_match_in_period=True, 
        returning="date",
        date_format="YYYY-MM", 
        return_expectations={"date": {"latest": "index_date"}},
    ),
    ## diabetes
    diabetes=patients.with_these_clinical_events(
        diabetes,
        on_or_before="index_date",
        returning="binary_flag",
        return_expectations={"incidence": 0.20},
    ),
    ## hiv
    hiv=patients.with_these_clinical_events(
        hiv,
        on_or_before="index_date",
        returning="binary_flag",
        return_expectations={"incidence": 0.20},
    ),
    ## COVID test 
    first_positive_covid_test=patients.with_test_result_in_sgss(
        pathogen="SARS-CoV-2",
        test_result="positive",
        on_or_after="2020-02-01",
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={"date": {"earliest" : "2020-02-01"},
        "incidence" : 0.25},
    ),
    # OTHER VARIABLES 
    ## Health care worker status 
    hcw=patients.with_healthcare_worker_flag_on_covid_vaccine_record(returning='binary_flag', return_expectations=None), 
    )
    return confounding_variables
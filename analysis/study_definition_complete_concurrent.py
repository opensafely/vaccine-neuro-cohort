# Import necessary functions
from cohortextractor import (
    StudyDefinition,
    patients,
    codelist_from_csv,
    codelist,
    filter_codes_by_category,
    combine_codelists
)

# Import all codelists
from codelists import *

# Import the required data 

CONTROLS = "output/matched_matches_concurrent.csv"

# Import Variables 

## confounding variables 
from confounding_variables import generate_confounding_variables
confounding_variables = generate_confounding_variables(index_date_variable="case_index_date")

## outcome variables 
from outcome_variables import generate_outcome_variables
outcome_variables = generate_outcome_variables(index_date_variable="case_index_date")

# Specify study definition

study = StudyDefinition(
    # configure the expectations framework
    default_expectations={
        "date": {"earliest": "1900-01-01", "latest": "today"},
        "rate": "uniform",
        "incidence" : 0.2
    },

     # select the study population
    population=patients.which_exist_in_file(CONTROLS), 

    # start of observation period (note, needs to be called index date)
    index_date="2020-12-08", # note should be ignored when using case_index_date 

    # import the case index date 
    case_index_date=patients.with_value_from_file(
        CONTROLS, 
        returning="case_index_date", 
        returning_type="date"), 

    # CONFOUNDING VARIABLES  
    **confounding_variables, 

    # OUTCOME VARIABLES  
    **outcome_variables, 

    # TIME-VARYING SELECTION VARIABLES 
    ## To be applied manually to the control pool as cannot be specified pre-match 

    ### pregnancy 
    pregnancy=patients.with_these_clinical_events(
    preg,
    returning="binary_flag",
    find_last_match_in_period=True,
    between=["case_index_date - 274 days", "case_index_date"],
    return_expectations={"incidence": 0.01}
    ),

    ### has one year of baseline time
    has_baseline_time=patients.registered_with_one_practice_between(
       start_date="case_index_date - 1 year",
       end_date="case_index_date",
       return_expectations={"incidence": 0.95},
    ),

    ### died before index
    has_died=patients.died_from_any_cause(
      on_or_before="case_index_date",
      returning="binary_flag",
    ),

    ### died after index (extracted as used as a matching variable, so needs to exist)
    death_date=patients.died_from_any_cause(
        on_or_after="case_index_date",
        returning="date_of_death",
        date_format="YYYY-MM-DD", 
        return_expectations={
            "date": {
                "earliest": "2020-12-08",  
                "latest": "2021-05-11", }, 
                "incidence": 0.01 },
    ),

    ### deregistered after index (extracted as used as a matching variable, so needs to exist)
    dereg_date=patients.date_deregistered_from_all_supported_practices(
        on_or_after="case_index_date", date_format="YYYY-MM",
    ),

    ## RESIDENTIAL STATUS 
    ### known care home 
    #### type of care home
    care_home_type=patients.care_home_status_as_of(
        "case_index_date",
        categorised_as={
            "CareHome": """
              IsPotentialCareHome
              AND LocationDoesNotRequireNursing='Y'
              AND LocationRequiresNursing='N'
            """,
            "NursingHome": """
              IsPotentialCareHome
              AND LocationDoesNotRequireNursing='N'
              AND LocationRequiresNursing='Y'
            """,
            "CareOrNursingHome": "IsPotentialCareHome",
            "PrivateHome": "NOT IsPotentialCareHome",
            "": "DEFAULT",
        },
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"CareHome": 0.30, "NursingHome": 0.10, "CareOrNursingHome": 0.10, "PrivateHome":0.45, "":0.05},},
        },
    ),
    #### has any value for the above 
    known_care_home=patients.satisfying(
        """care_home_type""",
        return_expectations={"incidence": 0.99},
    ),

    ## index of multiple deprivation, estimate of SES based on patient post code 
    imd=patients.categorised_as(
        {
            "0": "DEFAULT",
            "1": """index_of_multiple_deprivation >=1 AND index_of_multiple_deprivation < 32844*1/5""",
            "2": """index_of_multiple_deprivation >= 32844*1/5 AND index_of_multiple_deprivation < 32844*2/5""",
            "3": """index_of_multiple_deprivation >= 32844*2/5 AND index_of_multiple_deprivation < 32844*3/5""",
            "4": """index_of_multiple_deprivation >= 32844*3/5 AND index_of_multiple_deprivation < 32844*4/5""",
            "5": """index_of_multiple_deprivation >= 32844*4/5 AND index_of_multiple_deprivation < 32844""",
        },
        index_of_multiple_deprivation=patients.address_as_of(
            "case_index_date",
            returning="index_of_multiple_deprivation",
            round_to_nearest=100,
        ),
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "0": 0.05,
                    "1": 0.19,
                    "2": 0.19,
                    "3": 0.19,
                    "4": 0.19,
                    "5": 0.19,
                }
            },
        },
    ),
) 














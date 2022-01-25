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

# Import Variables 

## vaccine variables 
from vaccine_variables import generate_vaccine_variables
vaccine_variables = generate_vaccine_variables(index_date="index_date")

## matching variables 
from matching_variables import generate_matching_variables
matching_variables = generate_matching_variables(index_date="index_date")

# Specify study definition

study = StudyDefinition(
    # configure the expectations framework
    default_expectations={
        "date": {"earliest": "1900-01-01", "latest": "today"},
        "rate": "uniform",
        "incidence" : 0.2
    },

    # start of observation period (note, needs to be called index date)
    index_date="2020-12-08", 

     # select the study population
     # note that this is the pool of potential unexposed concurrent controls 
     # criteria relevant to their index dates (ie, vaccination and vital status), is determined in the matching action 

    population=patients.satisfying(
        """
        (age >= 18 AND age < 105) 
        AND (sex = "M" OR sex = "F") 
        AND NOT unexposed_has_died
        """,
    ),
    
    # VACCINATION VARIABLES  
    **vaccine_variables, 

    # MATCHING VARIABLES  
    **matching_variables, 

    # SELECTION VARIABLES 
    ### sex 
    sex=patients.sex(
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"M": 0.49, "F": 0.51}},
        }
    ),

    # TIME-VARYING SELECTION VARIABLES 
    ## These variables are EITHER 1) defined within a specific time frame relative to the patient vaccination date 
    ## OR 2) defined as before/after/on the patient vaccination date, but they return something other than a date 
    ## For controls, they need to be extracted and applied after matching as controls are assigned the patient vaccination date 
    ## It is most efficient to extract these separately for exposed and controls, as they are not needed for the controls yet,
    ## and we don't want to spend time matching ineligble exposed people  

    ## For the controls, the only criteria that can be applied before the assignment of the case index date is age, sex,  death and dereg criteria 

    unexposed_has_died=patients.died_from_any_cause(
        on_or_before="index_date",
        returning="binary_flag",
        date_format="YYYY-MM-DD", 
    ),

    death_date=patients.died_from_any_cause(
        on_or_after="index_date",
        returning="date_of_death",
        date_format="YYYY-MM-DD", 
        return_expectations={
            "date": {
                "earliest": "2020-12-08",  
                "latest": "2021-05-11", }, 
                "incidence": 0.01 },
    ),

    dereg_date=patients.date_deregistered_from_all_supported_practices(
        on_or_after="index_date", date_format="YYYY-MM",
    ),

) 











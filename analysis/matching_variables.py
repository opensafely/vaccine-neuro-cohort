from cohortextractor import filter_codes_by_category, patients, combine_codelists
from codelists import *
from datetime import datetime, timedelta


def generate_matching_variables(index_date_variable):
    matching_variables = dict(

    ## age 
    age=patients.age_as_of(
        f"{index_date_variable}",
        return_expectations={
            "rate": "universal",
            "int": {"distribution": "population_ages"},
        },
    ),
    ## age group (for cohort matching)
    matching_age= patients.categorised_as(
        {   
            "0": "DEFAULT",
            "<65": """ age < 65 """, 
            "65-69": """ age >=  65 AND age < 70""",
            "70-74": """ age >=  70 AND age < 75""",
            "75-79": """ age >=  75 AND age < 80""",
            "80+": """ age >=  80 """,
        },
        return_expectations={
            "rate":"universal",
            "category": {"ratios": {"<65":0.5, "65-69": 0.1,"70-74": 0.1, "75-79": 0.1, "80+":0.2}}
        },
    ),
    ## geographical region 
    stp=patients.registered_practice_as_of(
        f"{index_date_variable}",
        returning="stp_code",
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "STP1": 0.1,
                    "STP2": 0.1,
                    "STP3": 0.1,
                    "STP4": 0.1,
                    "STP5": 0.1,
                    "STP6": 0.1,
                    "STP7": 0.1,
                    "STP8": 0.1,
                    "STP9": 0.1,
                    "STP10": 0.1,
                }
            },
        },
    ), 

    )
    return matching_variables

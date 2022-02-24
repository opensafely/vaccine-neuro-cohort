import pandas as pd
from osmatching import match

# CONCURRENT CONTROLS
match(
    case_csv="input_exposed",
    match_csv="input_concurrent_controls",
    matches_per_case=5,
    match_variables={
        "matching_age": "category",
        "stp": "category",
    },
    index_date_variable="case_index_date", 
    replace_match_index_date_with_case="no_offset", 
    date_exclusion_variables={
        "death_date": "before",
        "dereg_date": "before",
        "first_any_vaccine_date": "before",
    },
    indicator_variable_name="exposed", 
    output_suffix="_concurrent",
    output_path="output",
)

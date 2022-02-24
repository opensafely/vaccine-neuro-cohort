/*==============================================================================
DO FILE NAME:				apply_exclusion_criteria
PROJECT:					vaccine safety (cohort)
DATE: 						26 Jan 2022  
AUTHOR:						aschultze 
								
DESCRIPTION OF FILE:		merges in additional control covariates 
							conduct checks on key variables 
							applies exclusion criteria that rely on 
							assigned case index dates 

DATASETS USED:				output/input_cases_concurrent.csv
							output/matched_matches_concurrent.csv 
OUTPUT, SERVER ONLY 		output/concurrent_cohort.dta 
							logfile, printed to folder output/logs 
OUTPUT, REDACT + RELEASE	check_report.txt 
							
==============================================================================*/

/* HOUSEKEEPING===============================================================*/

* create folders that do not exist on server 
capture	mkdir "`c(pwd)'/output/logs"
capture	mkdir "`c(pwd)'/output/tables"

* set ado path
adopath + "`c(pwd)'/analysis/extra_ados"

* open a log file
cap log close
log using "`c(pwd)'/output/logs/01_apply_exclusion_criteria.log", replace 

* IMPORT DATA=================================================================*/ 

* import data on the controls and cases and convert to dta (for merging)
import delimited `c(pwd)'/output/matched_combined_concurrent.csv, clear  
save `c(pwd)'/output/matched_combined_concurrent.dta, replace

*import additional covariates for control
import delimited `c(pwd)'/output/input_complete_concurrent.csv, clear  

* MERGE DATA==================================================================*/ 
* note, patient ID in the using file is not unique as some cases can also be controls 
* note, patient ID should be unique in the master data, because sampling without replacement 
merge 1:m patient_id using `c(pwd)'/output/matched_combined_concurrent.dta

* SENSE CHECKS ===============================================================*/ 
di "check number of duplicates (cases who are also controls)"
duplicates report patient_id 

di "confirm there are no duplicates in set_id (all controls should be unvaccinated)"
duplicates report patient_id set_id 

di "check number of matches (note, those without matches still included)" 
tab match_counts, m

di "check matching. note, would expect all controls to be matched"
tab _m, m

di "check number of controls"
tab exposed, m

* placeholder - need to add a series of sense checks here (potentially)

* APPLY  EXCLUSION CRITERIA===================================================*/ 
* Exclusion criteria should already be applied to the cases
* Time-updated exclusion criteria need to be applied to the controls 
* These criteria relate to pregnancy, applied here
* also need to apply history of outcome for each outcome, but that is done per analysis

* need at least one control 
di "Number of people dropped due to no controls found during original matching" 
count if match_counts < 1 
drop if match_counts < 1 
tab match_counts

* need to not be pregnant at index date 
tab preg 

di "number of pregnant cases (should be zero, as already applied)"
count if preg == 1 & exposed == 1

di "number of pregnant controls"
count if preg == 1 & exposed == 0

di "dropped due to pregnancy at index"
drop if preg == 1 

* recreate a match_count after applying exclusion criteria 
egen new_count = count(patient_id), by (set_id)
gen control_count = new_count - 1 
replace control_count = . if exposed == 0 

gen difference = 1 if match_counts != control_count
di "number of cases where the number of controls reduced" 
count if difference == 1 
di "number of cases now with less than 1 control"
count if control_count < 1 

* need at least one control
di "number of people dropped due to no controls after applying exclusions"
drop if control_count < 1 

* DATA CLEANING===============================================================*/ 

* placeholder - discuss with Jemma how to implement/split 

* order key variables and sort by set ID 
sort set_id exposed 
order set_id patient_id exposed control_count 

* EXPORT RESULTS AS DTA=======================================================*/ 
save  `c(pwd)'/output/concurrent_cohort.dta, replace

* CLOSE LOG===================================================================*/ 

log close

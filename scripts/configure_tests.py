import os
thisLocation = os.path.dirname(os.path.abspath(__file__))
statpackage_location = thisLocation+

## Settings ##

# These are the spectra to test. The names map to the 
# input files as well as toy and signal injected spectra.
spectra = ["single_inclusive"]#,"combined_inclusive"]

# In case you generated several sets of toys for the 
# background spectrum, use this to specify which one you 
# want to use for the signal injection tests.
background_toy_ID = 0

# These are the mass points to test for each spectrum
mass_points = {
  "single_inclusive" : [200,220,225,250],
  "combined_inclusive" : [],
}

# These are the Gaussian widths to test at each mass point
# Expressed as a percentage.
gaussian_widths = [7, 10, 15]

## Fit related settings

# These are the functions to test.
# Options: "our3par","our4par", "our5par","UA2"
functions = ["our5par"]

# These are the SWIFT window sizes to test,
# specified as number of bins in half-width
swift_window_widths = [19]

# These are the fitting config files to use as templates
# for each spectrum.
# They should already contain fit ranges and correct SWIFT
# settings so that only the function and window width need
# to be changed.
template_config_path = thisLocation+"/../configs/search_phase_templates/"
template_configs = {
  "single_inclusive" : thisLocation+"SearchPhase_dijetgamma_single_trigger_inclusive.config"
  "combined_inclusive" : thisLocation+"configs/search_phase_templates/SearchPhase_dijetgamma_compound_trigger_inclusive.config"
}

## Paths ##

# Where should I make the new configs?
new_config_dir = thisLocation+"/../configs/search_phase_generated/"

# Locations for root files
location_toySpectra = thisLocation + "/../toy_spectra/"
location_signalInjectedSpectra = thisLocation + "/../signal_injected_spectra/"
location_final = thisLocation + "/home/kpachal/project/kpachal/DijetISR/Resolved2017/SignalInjection/"

# Shouldn't need this usually, but if you are using a toy background file 
# you didn't need yourself, the code needs to know what histogram to choose.
# Otherwise just set it to an empty string.
bkg_hist_name = "basicBkgFrom4ParamFit_fluctuated"

## Batch configuring ##
use_batch = True
batch_type = "slurm"
template_script = "batch_scripts/batchScript_template_CEDAR.sh"

# Location for batch submission scripts
location_batchscripts = thisLocation+"/batch_scripts/"
location_submissonscripts = thisLocation+"/submission_scripts/"


import os
thisLocation = os.path.dirname(os.path.abspath(__file__))

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
template_config_path = os.path.abspath(os.path.join("../configs/search_phase_templates/"))
template_configs = {
  "single_inclusive" : template_config_path+"/SearchPhase_dijetgamma_single_trigger_inclusive.config",
  "combined_inclusive" : template_config_path+"/SearchPhase_dijetgamma_compound_trigger_inclusive.config"
}

## Paths ##

# Where is the BayesianFramework package set up?
stat_dir = os.path.join(thisLocation,"../../BayesianFramework/")

# Where should I make the new configs?
new_config_dir = os.path.abspath(os.path.join(thisLocation,"../configs/search_phase_generated/"))

# Locations for root files
location_toySpectra = os.path.abspath(os.path.join(thisLocation,"../toy_spectra/"))
location_signalInjectedSpectra = os.path.abspath(os.path.join(thisLocation,"../signal_injected_spectra/"))
#location_final = "/home/kpachal/project/kpachal/DijetISR/Resolved2017/SignalInjection/"
location_final = os.path.abspath(os.path.join(thisLocation,"../fitted_results/"))


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
location_submissionscripts = thisLocation+"/submission_scripts/"

## Special cases ##

# Here we have optional manual overrides for special situations.

# If you have a mass point which is really close to the start of your search,
# it's going to need more than the usual 2.5 to 5 stat sigmas.
# You can override with the values to use here.

override_injection_sigmas = {
  200 : {
    "low_end" : 4.0,
    "high_end" : 10.0
  },
  220 : {
    "low_end" : 3.5,
    "high_end" : 8.0
  },
  225 : {
    "low_end" : 3.5,
    "high_end" : 7.0
  }
}






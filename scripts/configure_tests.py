import os

## Settings ##

# These are the spectra to test. The names map to the 
# input files as well as toy and signal injected spectra.
spectra = ["single_inclusive","combined_inclusive"]

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

# These are the functions to test
functions = ["our5par"]

# These are the SWIFT window sizes to test,
# specified as number of bins in half-width
swift_window_withs = [19]

## Paths ##

thisLocation = os.path.dirname(os.path.abspath(__file__))
location_toySpectra = thisLocation + "../toy_spectra/"
location_signalInjectedSpectra = thisLocation + "../signal_injected_spectra/"
location_final = thisLocation + "../fit_results/"

## Batch configuring ##

batch_type = "Slurm"


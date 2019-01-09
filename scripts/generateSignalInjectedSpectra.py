import ROOT
import sys,os
import glob

import configure_tests as config

# Get spectra to run on
spectra = config.spectra

# Get ID number of toy we want to use for background
toyID = config.background_toy_ID

# We need to make signal injected toys for each of them.
for spectrum in spectra :

  print "Beginning toy generation for spectrum",spectrum

  # Find files with toy spectra. 
  # There should be no ambiguity.
  toyFilesDir = config.location_toySpectra
  toyFiles = glob.glob(toyFilesDir+"/*"+spectrum+"*toy{0}".format(toyID)+"*.root")
  if len(toyFiles) == 1 :
    toyFile = toyFiles[0]
    print "Using file",toyFile,"for toy background distribution."
  else :
    print "Found wrong number of toy files!"
    print toyFiles
    exit(1)

  # Get spectrum of toys for background from the file.
  toyFile_read = ROOT.TFile.Open(toyFile,"READ")
  toy_histName = config.bkg_hist_name if config.bkg_hist_name else "background_toys"
  toy_background = toyFile_read.Get(toy_histName)
  toy_background.SetDirectory(0)
  toyFile_read.Close()
 
  # Make several tests at different normalisations for each signal mass and width.
  for sig_mass in config.mass_points[spectrum] :
    for sig_width in config.gaussian_widths :

      print "Making spectra for mass",sig_mass,"and width",sig_width,"%"
      # File to put distribution in
      outFileName = config.location_signalInjectedSpectra + "/signalInjectedBkg_{0}_mass{1}_width{2}.root".format(spectrum,sig_mass,sig_width)

      # Make the Gaussian as a TF1
      onesigma = float(sig_width)/100.0 * sig_mass
      gaussian = ROOT.TF1("signal","TMath::Gaus(x,{0},{1})".format(sig_mass,onesigma),sig_mass-3.0*onesigma, sig_mass+3.0*onesigma)

      # Make a simple Gaussian histogram normalised to 1 event
      # and matching analysis binning.
      sig_normalised = toy_background.Clone()
      sig_normalised.SetName("signal_normalised")
      sig_normalised.SetDirectory(0)
      sig_normalised.Reset()
      for ibin in range(1,sig_normalised.GetNbinsX()+1) :
        if (sig_normalised.GetBinLowEdge(ibin) >= sig_mass+3.0*onesigma) or (sig_normalised.GetBinLowEdge(ibin+1) <= sig_mass-3.0*onesigma) :
          sig_normalised.SetBinContent(ibin,0)
          sig_normalised.SetBinError(ibin,0)
        else :
          a = sig_normalised.GetBinLowEdge(ibin)
          b = sig_normalised.GetBinLowEdge(ibin+1)
          content = gaussian.Integral(a,b)
          sig_normalised.SetBinContent(ibin,content)
          sig_normalised.SetBinError(ibin,0)
      sig_normalised.Scale(1.0/sig_normalised.Integral())

      injected_spectra = []
      vals = []
      # Pick the numbers of events where a p-value of 0.01 is likely to occur.
      # For well-behaved points these values work well:
      scale_lowEnd = 2.5
      scale_highEnd = 5.0
      # For points close to the low end, these might not be big enough
      # Then the user can manually override them using the config.
      if sig_mass in config.override_injection_sigmas.keys() :
        scale_lowEnd = config.override_injection_sigmas[sig_mass]["low_end"]
        scale_highEnd = config.override_injection_sigmas[sig_mass]["high_end"]

      centerbin = toy_background.FindBin(sig_mass)
      print "in bin",centerbin,"bin content is",toy_background.GetBinContent(centerbin),"and error is",toy_background.GetBinError(centerbin)
      lowVal_centerbin = toy_background.GetBinError(centerbin)*scale_lowEnd
      highVal_centerbin = toy_background.GetBinError(centerbin)*scale_highEnd
      print "lowVal and highVal are",lowVal_centerbin,highVal_centerbin
      for step in range(20) :
        val = float(lowVal_centerbin) + float(step)/19.0 * (float(highVal_centerbin) - float(lowVal_centerbin))
        val = round(val)
        vals.append(val)
        this_sig = sig_normalised.Clone()
        this_sig.SetName("sigToScale")
        this_sig.SetDirectory(0)
        this_sig.Scale(val/sig_normalised.GetBinContent(centerbin))
        this_hist = toy_background.Clone()
        this_hist.SetName("background_injected_nSignal{0}".format(int(this_sig.Integral())))
        this_hist.SetDirectory(0)
        this_hist.Add(this_sig)
        injected_spectra.append(this_hist)

      # Create output file to save background, baseline signal template, and injected backgrounds.
      outFile_write = ROOT.TFile.Open(outFileName,"RECREATE")
      outFile_write.cd()
      toy_background.Write("background_toys")
      sig_normalised.Write()
      for injected_spectrum in injected_spectra :
        injected_spectrum.Write()
      outFile_write.Close()




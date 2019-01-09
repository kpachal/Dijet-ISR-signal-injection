import ROOT
import glob
from art.morisot import Morisot
from analysisScripts.searchphase import searchFileData

import configure_tests as config

# Initialize painter
myPainter = Morisot()
myPainter.setColourPalette("notSynthwave")
myPainter.setLabelType(2)
myPainter.setEPS(True)
myPainter.dodrawUsersText = True

CME = 13000

file_data = {}
for spectrum in config.spectra :
  file_data[spectrum] = {}
  for function in config.functions :
    file_data[spectrum][function] = {}
    for signal_width in config.gaussian_widths :
      file_data[spectrum][function][signal_width] = {}
      print "Beginning signal width",signal_width

      # This is the level on which we make the 2D plots. Analyse here.
      myDict = {}
      listOfResults = open("results_list.txt", 'w')

      # Get file contents
      for swift_window in config.swift_window_widths :
        myDict[swift_window] = {}
        for mass in config.mass_points[spectrum] :
          myDict[swift_window][mass] = {}

          fileNameFormat = config.location_final+"/*{0}*{1}*swiftWHW{3}*mass{4}*_width{2}*.root".format(spectrum,function,signal_width,swift_window,mass)
          files = glob.glob(fileNameFormat)

          # Retrieve data and store in myDict.
          for file in files :
            signalTokens = [i for i in file.split("_") if "nSigEvents" in i]
            nSignalInjected = eval(signalTokens[0].replace(".root","").replace("nSigEvents",""))

            try :
              this_data = searchFileData(file)
            except ValueError :
              print "No data created!"
              continue

            myDict[swift_window][mass][nSignalInjected] = this_data

      # myDict now contains everything we need to understand the results.
      # Analyse!
      for swift_window in config.swift_window_widths :
        for mass in config.mass_points[spectrum] :

          print "Window",swift_window,"and mass",mass,":"

          justAboveVal = None 
          justBelowVal = None

          # Graph of how p-value evolves as number of events go up
          pVal_evolution = ROOT.TGraph()

          # Loop through values injected and check p-vals
          index = -1
          for nSignal in sorted(myDict[swift_window][mass].keys()) :
            index = index+1
            data = myDict[swift_window][mass][nSignal]

            pval = data.bumpHunterPVal
            fit = data.basicBkgFromFit
            residual = data.residualHist
            didExcludeWindow = data.excludeWindow
            windowLow = None
            windowHigh = None
            if didExcludeWindow :
              windowLow = data.bottomWindowEdge
              windowHigh = data.topWindowEdge

            # Add point to graph
            pVal_evolution.SetPoint(index,nSignal,pval)

            # Check which side of 0.01 we are on.
            if pval > 0.01 :
              justBelowVal = nSignal
            else :
              justAboveVal = nSignal
              print "Found 0.01 point with nSignal",nSignal
              print "Just below is",justBelowVal
              break

          if not justAboveVal :
            print "Did not find a 0.01 point!"
            print "Last nEvents was",justBelowVal,"with p-value",myDict[swift_window][mass][nSignal].bumpHunterPVal

          myDict[swift_window][mass]["pValueGraph"] = pVal_evolution

      # Make summary output for this spectrum/function/signal width
      outfile_name = "summary_{0}_{1}_width{2}.root".format(spectrum,function,signal_width)
      outfile = ROOT.TFile.Open(outfile_name,"RECREATE")
      outfile.cd()
      for swift_window in sorted(myDict.keys()) :
        for mass in sorted(myDict[swift_window].keys()) :
          myDict[swift_window][mass]["pValueGraph"].Write("pvalue_vs_events_WHW{0}_mass{1}".format(swift_window,mass))
      outfile.Close()



      



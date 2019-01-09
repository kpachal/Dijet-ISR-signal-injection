#!/usr/bin/env python
import subprocess # So can use shell scripting in python
import os, sys
import re
import datetime

import configure_tests as config

## Various functions ##

def generate_config(template_config, spectrum, function, window_width, signal_width, signal_mass, number_signal) :

  # String for identifying this test.
  # Will be amended with specific histogram name (number of signal points) later,
  # but this is the one thing we are sharing configs for.
  test_name = "_".join(spectrum,function,"swiftWHW{0}".format(window_width))

  # Open modified config file (fout) for this test
  run_config = config.new_config_dir + '/SearchPhase_{0}.config'.format(test_name)
  print "Creating config",configName
  #fout = open(configName, 'w')

  # read in search phase config file as fin and replace
  # relevant fields with user input specified in the config
  #with open(config["searchPhaseConfig"], 'r') as fin:

def getFileKeys(file_name,dir="") :
  open_rootfile = ROOT.TFile.Open(file_name,"READ")
  open_rootfile.cd(dir)
  keys_list = sorted([key.GetName() for key in ROOT.gDirectory.GetListOfKeys()])
  open_rootfile.Close()
  return keys_list

def makeOutputDirs() :

  # Make dirs
  directories = [config.location_final,config.new_config_dir,config.location_batchscripts,config.location_submissionscripts]
  for directory in directories:
    if not os.path.exists(directory):
      os.makedirs(directory)  

def batchSubmit(batchcommand,stringForNaming) :

  # Perform fit and bump hunt on batch
  print batchcommand

  # Open batch script as fbatchin
  fbatchin = open(templatescript, 'r')
  fbatchindata = fbatchin.read()
  fbatchin.close()

  # open modified batch script (fbatchout) for writing
  batchtempname = '{0}/searchPhase_{1}.sh'.format(scriptArchive,stringForNaming)
  fbatchout = open(batchtempname,'w')
  fbatchoutdata = fbatchindata.replace("YYY",headdir) # In batch script replace YYY for path for whole package
  fbatchoutdata = fbatchoutdata.replace("ZZZ",batchcommand) # In batch script replace ZZZ for submit command
  fbatchoutdata = fbatchoutdata.replace("TIMEVAL","6:00:00")
  fbatchout.write(fbatchoutdata)
  modcommand = 'chmod 744 {0}'.format(batchtempname)
  subprocess.call(modcommand, shell=True)
  fbatchout.close()
  if "torque" in batchType :
    submitcommand = "qsub {0}".format(batchtempname)
  elif "slurm" in batchType :
    submitcommand = "sbatch {0}".format(batchtempname)
  else :
    print "Please define a batch submission command for your batch!"
    exit(0)

  print submitcommand
  subprocess.call(submitcommand, shell=True)

## Run code ##

# So that we don't get any run-time errors...
makeOutputDirs()

# Need to run one job for each file.
# Configs will vary by fit and spectrum,
# as well as signal test.

# We could use the same config for each signal
# test and set the file name and histogram name
# as run-time arguments, but better to have standalone
# configs for cross checking.

spectra = config.spectra
functions = config.functions
window_widths = config.swift_window_widths

gaussian_widths = config.gaussian_widths

for spectrum in spectra :

  # Masses to check depends on spectrum.
  gaussian_masses = config.mass_points[spectrum]

  # Search phase config to use as template
  template_config = config.template_configs[spectrum]  

  # Now go through each option we want to test.
  for function in functions :
    for window_width in window_widths :

      # Baseline (no-signal) fit
      run_config, test_name = generate_config(template_config, spectrum, function, window_width)      

      for gaussian_width in gaussian_widths :
        for mass in gaussian_masses :

          # Now need one further loop over signal injected histograms in file.
          infile = location_signalInjectedSpectra+"/signalInjectedBkg_{0}_mass{1}_width{2}.root".format(spectrum,mass,gaussian_width)
          keys = getFileKeys(infile)

          # Begin loop. For each, make unique config.
          for key in keys :
            if not "background_injected" in key :
              continue

            n_signal = key.split("_")[-1].replace("nSignal","")
            print "Testing signal number",n_signal

            # Make a config file.
            run_config, test_name = generate_config(template_config, spectrum, function, window_width, gaussian_width, mass, n_signal)




### Old stuff

now = datetime.datetime.now()
tag = "{0}.{1}.{2}".format(now.year,now.month,now.day)

tag = tag+"_scalesOnly" # in case you want more



# For running the search phase
useBatch = config.use_batch
templatescript = config.template_script
# Options "slurm","torque","condor"
batchType = config.batch_type
# Where will batch scripts go?
scriptArchive = "submission_scripts/{0}/".format(tag)

# Test importing uncertainties from search phase?
importFitUncerts = False

# expected limits
doExpected = True
nPETotal = 100 # Total number of pseudo-experiments to run for expected limit bands. Was 100, should be ~200.
nSplits = 5 # Number of divisions to split PEs into
nPEForExpected = nPETotal/nSplits # Calculating how many PEs per division (split)

#=====Where is the place to asetup?==
headdir = (os.getcwd()).split("/run")[0]+"/BayesianFramework/" # directory for whole package


## Function for handling batch submission



# Run the submission

if __name__=="__main__":
    

    # Loop over signals
    for Model in config["Signals"].keys():

      for Mass in sorted(config["Signals"][Model]):

        # Signal file
        signalFileName = config["signalFileNameTemplate"].format(Mass,Model)

        # Histogram in signal file
        signalHist=signalHistTemplate

        outName = "ZPrime_mZ{0}_gS{1}".format(Mass,Model)
        
        # open modified config file (fout) for writing

        configName = scriptArchive + '/setLimitsOneMassPoint_{0}_{1}.config'.format(spectrum,outName)
        print "Creating config",configName
        fout = open(configName, 'w')

        # read in search phase config file as fin and replace
        # relevant fields with user inout specified at top of this file.
        with open(config["searchPhaseConfig"], 'r') as fin:

          fout.write("##########################################\n# input/output for limit setting \n##########################################\n\n")
          fout.write("dataFileName {0}\n\n".format(config["searchPhaseResults"]))
          fout.write("dataHist  basicData\n\n")
          fout.write("signalFileName {0}\n\n".format(signalFileName))
          fout.write("nominalSignalHist {0}\n\n".format(signalHist))
          outname = "outputFileName "+outDir+"setLimitsOneMassPoint_{0}_{1}.root\n\n".format(spectrum,outName)
          fout.write(outname)
          fout.write("plotDirectory {0}\n\n".format(outDir))
          fout.write("plotNameExtension ZPrime\n\n")
          fout.write("signame     ZPrime\n\n")
          fout.write("##########################################\n")
          
          # Copy fitting info from search phase
          foundFitting = False
          for line in fin:
            if "fitting" in line :
              foundFitting = True
            if foundFitting :
              if "nPseudoExpFit" in line : continue
              fout.write(line)
              
          # Add limit info
          fout.write("##########################################\n# for limits\n##########################################\n\n")
          fout.write("nSigmas     3.\n\n")
          fout.write("doExpected    {0}\n\n".format( "true" if doExpected else "false"))
          fout.write("nPEForExpected    {0}\n".format(nPEForExpected))
          fout.write("PDFErrSize   {0}\n\n".format(PDFErrSize))
          fout.write("doFitError   {0}\n".format(doFitError))
          fout.write("nFitsInBkgError  {0}\n".format(nFitsInBkgError))
          fout.write("doExtendedRange    {0}\n\n".format(doExtendedRange))
          fout.write("doFitFunctionChoiceError  {0}\n".format(doFitFunctionChoiceError))
          fout.write("nFitsInFcnError     {0}\n".format(nFitsInFcnError))
          fout.write("nFitFSigmas   {0}\n\n".format(nFitFSigmas))
          fout.write("doLumiError   {0}\n".format(doLumiError))
          fout.write("luminosityErr   {0}\n\n".format(luminosityErr[spectrum]))
          fout.write("doBeam   {0}\n".format(doBeam))
          fout.write("BeamFile   {0}\n\n".format(BeamFile))
          fout.write("doJES     {0}\n\n".format(doJES))
          fout.write("doJER    {0}\n".format(doJER))
          fout.write("JERUnc   {0}\n\n".format(JERUnc))
          fout.write("doPhotonUnc  {0}\n".format(doPhotonUnc))
          fout.write("photonUnc  {0}\n\n".format(photonUnc[spectrum]))
          fout.write("doTrigEffUnc {0}\n".format(doTrigEffUnc[spectrum]))
          fout.write("trigEffUnc {0}\n\n".format(trigEffUnc))
          fout.write("doBTagSF  {0}\n".format(doBTagSF[spectrum]))
          fout.write("bTagSFFileName  {0}\n".format(bTagSFFileName))
          fout.write("bTagSFHistName  {0}\n\n".format(bTagSFHistName))
          fout.write("##########################################\n# JES\n##########################################\n\n")
          fout.write("useMatrices false\nuseTemplates true\n")
          sigHistNom = signalHist
          fout.write("nominalTemplateJES {0}\n\n".format(sigHistNom))
          fout.write("nComponentsTemp {0}\n".format(nComponentsTemp))
          fout.write("nameTemp1 {0}\n".format(sigHistNom.replace("Nominal","JET_GroupedNP_1")))
          fout.write("nameTemp2 {0}\n".format(sigHistNom.replace("Nominal","JET_GroupedNP_2")))
          fout.write("nameTemp3 {0}\n".format(sigHistNom.replace("Nominal","JET_GroupedNP_3")))
          fout.write("nameTemp4 {0}\n\n".format(sigHistNom.replace("Nominal","JET_EtaIntercalibration_NonClosure")))
          fout.write(JESString)

        fin.close()
        fout.close()

        # Interpret mass
        massString = Mass.strip("p")
        if len(massString)<2 : massString = massString+"00"
        else : massString = massString+"0"
        submitMass = eval(massString)

        # Setting command to be submitted (use tee to direc output to screen and to log file)
        command = ""
        if doPDFAccErr: # do PDF acceptance error
          command = "setLimitsOneMassPoint --config {0} --mass {1} --PDFAccErr {2}".format(configName, submitMass,PDFErrSize)
        else: # do not do PDF acceptance error
          command = "setLimitsOneMassPoint --config {0} --mass {1} ".format(configName,submitMass) #2>/dev/null 1>output_{2}.txt
        if importFitUncerts :
          command = command + " --takeFitErrsFromSearch"

        if useBatch :
          if doExpected:
            for p in range(nSplits): batchSubmit(command,"{0}_{1}".format(spectrum,outName), seedOffset+p+1)
          else: batchSubmit(command,"{0}_{1}".format(spectrum,outName))

        # Perform setLimitsOneMassPoint locally
        else:
          print command
          if doExpected:
            for p in range(nSplits):
              try:
                  #subprocess.call(command + " --seed " + str(seedOffset+p+1), shell=True)
                  pass
              except:
                  pass
          else:
              try:
                  #subprocess.call(command, shell=True)
                  pass
              except:
                  pass



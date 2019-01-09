#!/usr/bin/env python
import subprocess # So can use shell scripting in python
import os, sys
import re
import datetime

import configure_tests as config

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


#---------------------------
# Files and directories

#=====Signal histogram template ======"
inputs_dir = "/home/kpachal/project/kpachal/Datasets_DijetISR/"
signalHistTemplate= "m_jj_Nominal"

now = datetime.datetime.now()
tag = "{0}.{1}.{2}".format(now.year,now.month,now.day)

tag = tag+"_scalesOnly" # in case you want more

#=====Output file destination ======"
outDir = "/home/kpachal/project/kpachal/Datasets_DijetISR/limit_results_zprime/{0}/".format(tag)

#=====Run controls ==============="

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

#=====Actual configurations==

# Remove these here if you don't want to do all channels
toRun = [
#"compound_trigger_inclusive",
#"compound_trigger_nbtag2",
#"single_trigger_inclusive",
"single_trigger_nbtag2"
]

spectrumConfig = {

"compound_trigger_inclusive": {
    "searchPhaseResults": inputs_dir + "/search_official_results/SearchPhase_dijetgamma_compound_trigger_inclusive.root",
    "searchPhaseConfig": inputs_dir + "/search_official_results/SearchPhase_dijetgamma_compound_trigger_inclusive.config",
    "lumi": "76p6",
    "signalFileNameTemplate": inputs_dir + "limit_setting_sigsamples/Zprime_compound_trigger_inclusive_MGPy8EG_N30LO_A14N23LO_dmA_jja_Ph50_mR{0}_mD10_gS{1}_gD1.root",
    "Signals":{"p2":["p35", "p45", "p55", "p75", "p95",]},
},

"compound_trigger_nbtag2": {
    "searchPhaseResults": inputs_dir + "/search_official_results/SearchPhase_dijetgamma_compound_trigger_nbtag2.root",
    "searchPhaseConfig": inputs_dir + "/search_official_results/SearchPhase_dijetgamma_compound_trigger_nbtag2.config",
    "lumi": "76p6",
    "signalFileNameTemplate": inputs_dir + "limit_setting_sigsamples/Zprime_compound_trigger_nbtag2_MGPy8EG_N30LO_A14N23LO_dmA_jja_Ph50_mR{0}_mD10_gS{1}_gD1.root",
    "Signals":{"p2":["p35", "p45", "p55", "p75", "p95",]},
},

"single_trigger_inclusive": {
    "searchPhaseResults": inputs_dir + "/search_official_results/SearchPhase_dijetgamma_single_trigger_inclusive.root",
    "searchPhaseConfig": inputs_dir + "/search_official_results/SearchPhase_dijetgamma_single_trigger_inclusive.config",
    "lumi": "79p8",
    "signalFileNameTemplate": inputs_dir + "limit_setting_sigsamples/Zprime_single_trigger_inclusive_MGPy8EG_N30LO_A14N23LO_dmA_jja_Ph100_mR{0}_mD10_gS{1}_gD1.root",
    "Signals": {"p1":["p25","p35","p45","p55"],
                "p2":["p25","p35","p45","p55","p75"],
                "p3":["p25","p3", "p35", "p4", "p45", "p5", "p55", "p75", "p95"]},
},

"single_trigger_nbtag2": {
    "searchPhaseResults": inputs_dir + "/search_official_results/SearchPhase_dijetgamma_single_trigger_nbtag2.root",
    "searchPhaseConfig": inputs_dir + "/search_official_results/SearchPhase_dijetgamma_single_trigger_nbtag2.config",
    "lumi": "79p8",
    "signalFileNameTemplate": inputs_dir + "limit_setting_sigsamples/Zprime_single_trigger_nbtag2_MGPy8EG_N30LO_A14N23LO_dmA_jja_Ph100_mR{0}_mD10_gS{1}_gD1.root",
    "Signals": {"p1":["p25","p35","p45","p55"],
                "p2":["p25","p35","p45","p55","p75"],
                "p3":["p25","p3", "p35", "p4", "p45", "p5", "p55", "p75", "p95"]},

}
} # End spectrumConfig

##---------------------------
# Uncertainty quantities

#----PDF Error
doPDFAccErr = True # Set to True to use PDF Acceptance Error
#doPDFAccErr = False # Set to True to use PDF Acceptance Error
PDFErrSize = 0.01

#---Fit function Error
#doFitError="true"
doFitError="false"
nFitsInBkgError=100
doExtendedRange="false"

#----Fit Function choice error
#doFitFunctionChoiceError="true"
doFitFunctionChoiceError="false"
nFitsInFcnError=100
nFitFSigmas=1

#----Lumi Error
doLumiError="true"
#doLumiError="false"
luminosityErr = {
  "compound_trigger_inclusive" : 0.023,
  "compound_trigger_nbtag2" : 0.023,
  "single_trigger_inclusive" : 0.020,
  "single_trigger_nbtag2" : 0.020
}

#---Beam systematics
doBeam="false"
BeamFile="./inputs/BeamUncertainty/AbsoluteBEAMUncertaintiesForPlotting.root"

#--JES
#doJES="true"
doJES="false"
useMatrices="false"
useTemplates="true"
nComponentsTemp=4
components = ["JET_GroupedNP_1","JET_GroupedNP_2","JET_GroupedNP_3","JET_EtaIntercalibration_NonClosure"]

JESString = '''
##--------------------------------------##
# nJES is number of extensions +1
nJES      7
extension1        __3down
extension2        __2down
extension3        __1down
extension4        __1up
extension5       __2up
extension6       __3up
'''

#--JER
doJER="true"
#doJER="false"
JERUnc=0.03

#--photon uncertainties
doPhotonUnc="true"
#doPhotonUnc="false"
photonUnc = {
  "compound_trigger_inclusive" : 0.014,
  "compound_trigger_nbtag2" : 0.014,
  "single_trigger_inclusive" : 0.020,
  "single_trigger_nbtag2" : 0.020
}

#--trigger efficiency
doTrigEffUnc = {
  "compound_trigger_inclusive" : "true",
  "compound_trigger_nbtag2" : "true",
  "single_trigger_inclusive" : "false",
  "single_trigger_nbtag2" : "false"
}
trigEffUnc = 0.030

#--b-tagging SF uncertainties
doBTagSF = {
  "compound_trigger_inclusive" : "false",
  "compound_trigger_nbtag2" : "true",
  "single_trigger_inclusive" : "false",
  "single_trigger_nbtag2" : "true"
}
bTagSFFileName=headdir+"source/Bayesian/share/bSF_uncertainty.root"
bTagSFHistName="bSF_uncertainty_relative"

#----------------------------------
# ***** End of User specifies *****
#----------------------------------

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


#-------------------------------------
# Performing Step 2: Limit setting for each model & mass using setLimitsOneMassPoint.cxx
#-------------------------------------

statspath = os.getcwd() # path used in outputFileName in config

if __name__=="__main__":

  for spectrum, config in spectrumConfig.iteritems():
  
    # Only do the specified ones
    if not spectrum in toRun :
      continue
    
    # Make dirs
    directories = [outDir,scriptArchive]
    for directory in directories:
      if not os.path.exists(directory):
        os.makedirs(directory)

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



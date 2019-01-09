#!/usr/bin/env python
import subprocess # So can use shell scripting in python
import os, sys
import re
import datetime

import configure_tests as config

## General ##

now = datetime.datetime.now()
tag = "{0}.{1}.{2}".format(now.year,now.month,now.day)

# So that we don't get any run-time errors...
directories = [config.location_final,config.new_config_dir,config.location_batchscripts,config.location_submissionscripts]
for directory in directories:
  if not os.path.exists(directory):
    os.makedirs(directory) 

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

# Configuring batch
useBatch = config.use_batch
templatescript = config.template_script
# Options "slurm","torque","condor"
batchType = config.batch_type
# Where will batch scripts go?
location_batchscripts = config.location_batchscripts

## Define various functions ##

def generate_config(template_config, spectrum, function, window_width, signal_width=-1, signal_mass=-1, number_signal=-1) :

  has_signal = False
  if signal_mass > 0 and signal_width > 0 and number_signal > 0 :
    has_signal = True  

  # String for identifying this test.
  # Will be amended with specific histogram name (number of signal points) later,
  # but this is the one thing we are sharing configs for.
  test_name = "_".join(spectrum,function,"swiftWHW{0}".format(window_width))
  if has_signal :
    name_ext = "_".join("mass{0}".format(signal_mass),"width{0}".format(signal_width),"nSigEvents{0}".format())
    test_name = test_name+name_ext

  # Details for setting up job
  if has_signal :
    input_name = location_signalInjectedSpectra+"/signalInjectedBkg_{0}_mass{1}_width{2}.root".format(spectrum,mass,gaussian_width)
    input_hist = "background_injected_nSignal{0}".format(int(number_signal))    
  else :
    # Pick any one of them, they are identical.
    input_options = glob.glob(location_signalInjectedSpectra+"/*"+spectrum+"*")
    input_name = input_options[0]
    input_hist = "background_toys"
  output_name = location_final+"/searchResult_{0}.root"+test_name

  # Open modified config file (fout) for this test
  run_config = config.new_config_dir + '/SearchPhase_{0}.config'.format(test_name)
  print "Creating config",run_config
  fout = open(run_config, 'w')

  # Read in search phase config file as fin and replace
  # relevant fields with user input specified in the config
  with open(template_config, 'r') as fin:
    fout.write("""##########################################\n
                  # Automatic config for signal injection search\n
                  ##########################################\n\n""")
    for line in fin:
      if "inputFileName" in line :
        line = "inputFileName\t{0}\n".format(input_name)
      if "dataHist" in line :
        line = "dataHist\t{0}\n".format(input_hist)
      if "outputFileName" in line :
        line = "outputFileName\n{0}\n".format(output_name)
      if "functionCode" in line :
        line = "functionCode"
      fout.write(line)    

    fin.close()
    fout.close()

  return run_config, test_name

def getFileKeys(file_name,dir="") :
  open_rootfile = ROOT.TFile.Open(file_name,"READ")
  open_rootfile.cd(dir)
  keys_list = sorted([key.GetName() for key in ROOT.gDirectory.GetListOfKeys()])
  open_rootfile.Close()
  return keys_list

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
  fbatchoutdata = fbatchindata.replace("YYY",config.stat_dir)
  fbatchoutdata = fbatchoutdata.replace("ZZZ",batchcommand)
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

# No need for uncertainties, so run with --noDE option
run_command = "SearchPhase --config {0} --noDE"

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

      # Submit jobs

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

            # Submit jobs


### Old stuff

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



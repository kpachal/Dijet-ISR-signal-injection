#!/usr/bin/env python
import subprocess # So can use shell scripting in python
import os, sys
import datetime
import glob
import ROOT

import configure_tests as config
from start_pars_80fb import startParDict

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

# These are the function codes for fitting,
# translating user config into run config
functionLoopDict = {
  "our5par" : {
    "functioncode" : 7,
    "npar" : 5
  },
  "our4par" : {
    "functioncode" : 4,
    "npar" : 4
  },
  "UA2" : {
    "functioncode" : 1,
    "npar" : 4
  },
  "our3par" : {
    "functioncode" : 9,
    "npar" : 3
  }
}

## Define various functions ##

def generate_config(template_config, spectrum, function, window_width, signal_width=-1, signal_mass=-1, number_signal=-1) :

  has_signal = False
  if signal_mass > 0 and signal_width > 0 and number_signal > 0 :
    has_signal = True  

  # String for identifying this test.
  # Will be amended with specific histogram name (number of signal points) later,
  # but this is the one thing we are sharing configs for.
  test_name = "_".join([spectrum,function,"swiftWHW{0}".format(window_width)])
  if has_signal :
    name_ext = "_".join(["mass{0}".format(signal_mass),"width{0}".format(signal_width),"nSigEvents{0}".format(number_signal)])
    test_name = test_name+"_"+name_ext

  # Details for setting up job
  if has_signal :
    input_name = config.location_signalInjectedSpectra+"/signalInjectedBkg_{0}_mass{1}_width{2}.root".format(spectrum,mass,gaussian_width)
    input_hist = "background_injected_nSignal{0}".format(int(number_signal))    
  else :
    # Pick any one of them, they are identical.
    input_options = glob.glob(config.location_signalInjectedSpectra+"/*"+spectrum+"*")
    input_name = input_options[0]
    input_hist = "background_toys"
  output_name = config.location_final+"/searchResult_{0}.root"+test_name

  # Details for fitting
  func_code = functionLoopDict[function]["functioncode"]
  npar = functionLoopDict[function]["npar"]
  startPars = startParDict[function][spectrum.split("_")[-1]]

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
      elif "dataHist" in line :
        line = "dataHist\t{0}\n".format(input_hist)
      elif "outputFileName" in line :
        line = "outputFileName\t{0}\n".format(output_name)
      elif "functionCode" in line :
        line = "functionCode\t{0}\n".format(func_code)
      elif "nParameters" in line :
        line = "nParameters\t{0}\n".format(npar)
      # Want to keep the right number of parameters
      if "parameter1" in line :
        line = ""
        for par in sorted(startPars.keys()) :
          line = line + "{0} {1}\n".format(par,startPars[par])
      elif "parameter" in line :
        continue
      elif "doAlternateFunction" in line :
        line = "doAlternateFunction     false\n"
      elif "swift_nBinsLeft" in line :
        line = "swift_nBinsLeft\t{0}\n".format(window_width)
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
  batchtempname = '{0}/searchPhase_{1}.sh'.format(config.location_batchscripts,stringForNaming)
  fbatchout = open(batchtempname,'w')
  fbatchoutdata = fbatchindata.replace("YYY",config.stat_dir)
  fbatchoutdata = fbatchoutdata.replace("ZZZ",batchcommand)
  fbatchoutdata = fbatchoutdata.replace("TIMEVAL","2:00:00")
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

      command = run_command.format(run_config)

      # Submit jobs
      # Submit jobs
      # if useBatch :
      #   batchSubmit(command,test_name)
      # else:
      #   subprocess.call(command, shell=True)      

      for gaussian_width in gaussian_widths :
        for mass in gaussian_masses :

          # Now need one further loop over signal injected histograms in file.
          infile = config.location_signalInjectedSpectra+"/signalInjectedBkg_{0}_mass{1}_width{2}.root".format(spectrum,mass,gaussian_width)
          keys = getFileKeys(infile)

          # Begin loop. For each, make unique config.
          for key in keys :
            if not "background_injected" in key :
              continue

            n_signal = key.split("_")[-1].replace("nSignal","")

            # Make a config file.
            run_config, test_name = generate_config(template_config, spectrum, function, window_width, gaussian_width, mass, n_signal)

            command = run_command.format(run_config)

            # Submit jobs
            if useBatch :
              batchSubmit(command,test_name)
            else:
              subprocess.call(command, shell=True)



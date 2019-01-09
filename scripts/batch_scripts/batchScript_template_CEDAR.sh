#! /bin/bash
#
# Script for CEDAR
# This be submitted to a batch queue and run as a container.
# See also this link on how to submit to batch queues
# https://twiki.atlas-canada.ca/bin/view/AtlasCanada/ATLASLocalRootBase2#Batch_Jobs
#

# site specific lines (eg particular to Compute Canada)
# 10 hours for these, for now.
#SBATCH --time=TIMEVAL
#SBATCH --account=def-vetm
#SBATCH --job-name=singularity_test
##SBATCH -p main
##SBATCH --ntasks=1

# These are ComputeCanada specific setups
module load singularity
source /project/atlas/Tier3/AtlasUserSiteSetup.sh

# These are additional options to singularity - examples
# export ALRB_CONT_OPTS="$ALRB_CONT_OPTS --debug"
# export ALRB_CONT_CMDOPTS="$ALRB_CONT_CMDOPTS whatever-option-you-want"

# specify what you want to do immediately after setupATLAS and before the job
export ALRB_CONT_POSTSETUP="pwd; whoami; date; hostname -f; date -u"

# specify the run job here; it can be a script too
#  this example sets up a release and prints the env before exiting
export ALRB_CONT_RUNPAYLOAD="""
echo 'starting job.';
cd YYY;
asetup --restore;
cd ../run;
source ../BayesianFramework/build/x86_64-centos6-gcc62-opt/setup.sh;
ZZZ
"""

# setupATLAS -c <container> which will run and also return the exit code
#  (setupATLAS is source $ATLAS_LOCAL_ROOT_BASE/user/atlasLocalSetup.sh)
setupATLAS -c slc6
exit $?


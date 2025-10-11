#!/bin/bash

#SBATCH --time=10:00:00
#SBATCH --mem=120G

# Specify a job name:
#SBATCH -J generate_iclr_data
#SBATCH -o %x-%j.out

# run command from safe/ directory, with command `sbatch demos/run_iclr_workflow.sh`

# Set up the environment by loading modules
module load cuda cudnn
module --ignore_cache load "conda"

# Run a script
conda init bash
conda activate faireenvconda
python demos/iclr_workflow.py

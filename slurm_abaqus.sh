#!/bin/bash

#SBATCH --mail-user=zhangzia@ssh1.tnt.uni-hannover.de
#SBATCH --mail-type=ALL

#SBATCH --job-name=abqsimul
#SBATCH --output=slurm-%j-out.txt

#  Limited to 12 hours
#SBATCH --time=12:00:00
#SBATCH --partition=cpu_short
#SBATCH --nodes=1
#SBATCH --cpus-per-task=32
#SBATCH --ntasks=1

#  48GB RAM memory per node reservated 
#SBATCH --mem=96G

#  working directory
cd "/home/zhangzia/Schreibtisch/studienarbeit/investigation/material/5E10"

# run abaqus script
python3 run_parametrestudy.py
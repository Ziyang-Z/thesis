#!/bin/bash
########################################################################################################################
#  Studienarbeit Ziyang Zhang
########################################################################################################################
#SBATCH --mail-user=zzyworkhardforfuture@gmail.com
#SBATCH --mail-type=ALL

#SBATCH --job-name=abqsimul
#SBATCH --output=slurm-%j-out.txt

#  Limited to 72 hours
#SBATCH --time=00:00:00
#SBATCH --partition=cpu_cluster_long
#SBATCH --nodes=1
#SBATCH --cpus-per-task=32
#SBATCH --ntasks=1

#  48GB RAM memory per node reservated 
#SBATCH --mem=96G

#  working directory
cd "/home/zhangzia/Schreibtisch/studienarbeit/32cpu"

/prog/abaqus/2020/bin/abaqus cae noGUI=script.py

#  /prog/abaqus/2020/bin/abaqus analysis job=Job-1.inp background cpu=32


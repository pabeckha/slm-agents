#!/bin/sh
#BSUB -J gpu_test
#BSUB -q gpua40
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=4GB]"
#BSUB -M 4GB
#BSUB -W 00:05
#BSUB -o logs/gpu_test_%J.out
#BSUB -eo logs/gpu_test_%J.err

module load cuda/12.6.3
echo "Host: $(hostname)"
echo "Date: $(date)"
nvidia-smi
echo "Done"

#!/bin/bash
#SBATCH --nodes 1
#SBATCH --ntasks-per-node 1
#SBATCH --cpus-per-task 1
#SBATCH --mem 12000
#SBATCH --time 30:00:00
#SBATCH --array=1-100

srun /home/hartevel/bin/Rosetta/main/source/bin/rosetta_scripts.linuxiccrelease @flags -out:file:silent des_${SLURM_ARRAY_TASK_ID} 
#srun /work/upcorreia/bin/rosetta_future/stable/RosettaWeekly/rosetta_scripts.linuxiccrelease @flags -out:file:silent des_${SLURM_ARRAY_TASK_ID}

echo "CASTOR: RUN FINISHED"

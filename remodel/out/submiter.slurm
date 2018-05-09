#!/bin/bash
#SBATCH --nodes 1
#SBATCH --ntasks-per-node 1
#SBATCH --cpus-per-task 1
#SBATCH --mem 10000
#SBATCH --time 10:00:00
#SBATCH --array=1-500

srun /home/hartevel/bin/Rosetta/main/source/bin/remodel.linuxiccrelease -s ../in/f_temlate -remodel:blueprint ../in/blueprint.bpf -no_optH false -out:nstruct 5 -chain A -ex1 -ex2 -insert_segment_from_pdb ../in/f_insert.pdb -out:file:silent sampling_conf_${SLURM_ARRAY_TASK_ID}

echo "CASTOR: RUN FINISHED"
